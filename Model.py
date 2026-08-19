import os
import psycopg2
from Field import Field

registry = {}

class ModelMeta(type):
    """Metaclass to collect fields and register models."""
    def __new__(mcs, name, bases, attrs):
        # We don't want to register the base 'Model' class itself
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)

        # 1. Collect all Field instances declared on the class
        _fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                _fields[key] = value

        # Save the collected fields back to the class attributes for easy access later
        attrs['_fields'] = _fields

        # 2. Derive the table name (default to lowercase class name if not provided)
        table_name = attrs.get('_table', name.lower())
        attrs['_table'] = table_name

        # Create the actual class
        new_class = super().__new__(mcs, name, bases, attrs)

        # 3. Register the model in the global registry
        registry[table_name] = new_class

        return new_class

class Model(metaclass=ModelMeta):
    """Base class that developers will inherit from."""

    def __init__(self, **kwargs):
        # Allow instantiation like User(name="Alice", age=30)
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)

    @classmethod
    def create_table(cls, conn):
        # 1. Determine table name (lowercase class name + 's' is standard convention)
        table_name = cls.__name__.lower() + "s"
        if table_name in registry:
            raise Exception(f"Table '{table_name}' already exists!")

        columns = []
        values = []

        # 2. Introspect the class: Loop through the attributes the developer wrote
        for attr_name, field_obj in cls.__dict__.items():
            # Only process attributes that are our ORM Fields
            if isinstance(field_obj, Field):
                # Build the SQL string for this specific column
                col_def = f"{attr_name} {field_obj.column_type}"
                if field_obj.primary_key:
                    col_def += " PRIMARY KEY"
                if field_obj.unique:
                    col_def += " UNIQUE"
                if field_obj.not_null:
                    col_def += " NOT NULL"
                if field_obj.default is not None:
                    values.append(field_obj.default)
                    col_def += " DEFAULT %s"

                columns.append(col_def)

        # 3. Assemble the final CREATE TABLE query
        columns_sql = ",\n    ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {columns_sql}\n);"

        print(f"\n--- Generated SQL for {cls.__name__} ---\n{sql}\n-----------------------------")

        # 4. Execute the query
        with conn.cursor() as curs:
            try:
                curs.execute(sql, values)
                conn.commit()
                print(f"Table '{table_name}' successfully verified/created!")
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error creating table '{table_name}': {error}")
                conn.rollback()