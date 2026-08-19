import os
import psycopg2
from Field import Field


class Model:
    """Base class that developers will inherit from."""

    @classmethod
    def create_table(cls, conn):
        # 1. Determine table name (lowercase class name + 's' is standard convention)
        table_name = cls.__name__.lower() + "s"
        # todo check existing? https://stackoverflow.com/questions/20582500/how-to-check-if-a-table-exists-in-a-given-schema

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