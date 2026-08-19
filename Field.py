import os
import psycopg2
from dotenv import load_dotenv

# ==========================================
# 1. ORM FIELD DEFINITIONS
# ==========================================
class Field:
    """Base class for all database fields."""
    def __init__(self, column_type, primary_key=False, unique=False, not_null=False, default=None):
        self.column_type = column_type
        self.primary_key = primary_key
        self.unique = unique
        self.default = default
        self.not_null = not_null

class Serial(Field):
    """Auto-incrementing integer (typically used for IDs)."""
    def __init__(self, primary_key=True, unique=False, not_null=False, default=None):
        super().__init__("SERIAL", primary_key=primary_key, unique=unique, not_null=not_null, default=default)

class Char(Field):
    """Varchar field."""
    def __init__(self, max_length=255, unique=False, not_null=False, default=None):
        super().__init__(f"VARCHAR({max_length})", unique=unique, not_null=not_null, default=default)

class Boolean(Field):
    """Boolean field."""
    def __init__(self, unique=False, not_null=False, default=None):
        super().__init__("BOOLEAN", unique=unique, not_null=not_null, default=default)

class Integer(Field):
    """Integer field."""
    def __init__(self, unique=False, not_null=False, default=None):
        super().__init__("INT", unique=unique, not_null=not_null, default=default)

class Timestamp(Field):
    """Timestamp field with a default of now."""
    def __init__(self, auto_now_add=False):
        default_sql = " DEFAULT CURRENT_TIMESTAMP" if auto_now_add else ""
        super().__init__(f"TIMESTAMP{default_sql}")

