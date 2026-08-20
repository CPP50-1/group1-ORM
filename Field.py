import os
import psycopg2
from dotenv import load_dotenv

# ==========================================
# 1. ORM FIELD DEFINITIONS
# ==========================================
class Field:
    """Base class for all database fields."""
    def __init__(self, column_type, primary_key=False, unique=False, not_null=False, default=None, python_type=None):
        self.column_type = column_type
        self.primary_key = primary_key
        self.unique = unique
        self.default = default
        self.not_null = not_null
        self.python_type = python_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if self.python_type is not None and not isinstance(value, self.python_type):
            raise TypeError(f"{self.name} must be an instance of {self.python_type.__name__}")
        instance.__dict__[self.name] = value

class Serial(Field):
    """Auto-incrementing integer (typically used for IDs)."""
    def __init__(self, primary_key=True, unique=False, not_null=False, default=None):
        super().__init__("SERIAL", primary_key=primary_key, unique=unique, not_null=not_null, default=default, python_type=int)

class Char(Field):
    """Varchar field."""
    def __init__(self, max_length=255, unique=False, not_null=False, default=None):
        super().__init__(f"VARCHAR({max_length})", unique=unique, not_null=not_null, default=default, python_type=str)

class Boolean(Field):
    """Boolean field."""
    def __init__(self, unique=False, not_null=False, default=None):
        super().__init__("BOOLEAN", unique=unique, not_null=not_null, default=default, python_type=bool)

class Integer(Field):
    """Integer field."""
    def __init__(self, unique=False, not_null=False, default=None):
        super().__init__("INT", unique=unique, not_null=not_null, default=default, python_type=int)

class Timestamp(Field):
    """Timestamp field with a default of now."""
    def __init__(self, unique=False, not_null=False, default='CURRENT_TIMESTAMP'):
        super().__init__("TIMESTAMP", unique=unique, not_null=not_null, default=default)

