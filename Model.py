import psycopg2
from psycopg2 import errors
from psycopg2.extensions import adapt

from Field import Field

registry = {}


class TableAlreadyExistsError(Exception):
    pass

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

        # Handle table name: either use the explicitely provided _table attribute, e.g people
        # or derive it from the class name (lower case and pluralized)
        if "_table" in attrs:
            table_name = attrs["_table"]
        else:
            table_name = name.lower()
            if not table_name.endswith("s"):
                table_name += "s"

        attrs['_table'] = table_name

        # check for duplicate model registrations
        if table_name in registry:
            raise TableAlreadyExistsError(
                f"Model for table '{table_name}' is already registered"
            )

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
        table_name = cls._table

        columns = []

        # We avoid using parameterized values for schema definitions, 
        # to avoid treating default values like CURRENT_TIMESTAMP as string literals
        # This is safe because we only use trusted values from the Field definitions, 
        # not user input.

        # 2. Introspect the class: Loop through the attributes the developer wrote
        
        # iterating over cls.__dict__ only finds fields declared directly on the current class
        # but miss fields inherited from a parent model, so we need to iterate on the fields
        for attr_name, field_obj in cls.fields.items():
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
                    if field_obj.default == "CURRENT_TIMESTAMP":
                        col_def += " DEFAULT CURRENT_TIMESTAMP"
                    else:
                        # safely quote literal defaults
                        # the default must come only from trusted model definitions
                        quoted_default = adapt(field_obj.default).getquoted().decode()
                        col_def += f" DEFAULT {quoted_default}"

                columns.append(col_def)

        # 3. Assemble the final CREATE TABLE query
        columns_sql = ",\n    ".join(columns)
        sql = f"""CREATE TABLE {table_name} (
            {columns_sql}
        )"""

        print(f"\n--- Generated SQL for {cls.__name__} ---\n{sql}\n-----------------------------")

        # 4. Execute the query
        # We do not suppress errors, we want the caller to be able to detect that table creation failed
        # Because we use CREATE TABLE, we can catch DuplicateTable errors from PostgreSQL
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        except errors.DuplicateTable as error:
            conn.rollback()
            raise TableAlreadyExistsError(
                f"Database table '{table_name}' already exists"
            ) from error
        except psycopg2.DatabaseError:
            conn.rollback()
            raise