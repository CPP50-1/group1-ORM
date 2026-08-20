import unittest

from Field import Char
from Model import Model


"""
Verifies the `Field` descriptor behavior.

- `User` defines a `name` field using `Char`.
- `User(name="Alice")` and `User(name="Bob")` test that constructor keyword arguments trigger `Field.__set__`.
- The first test confirms:
  - Each instance stores its own value.
  - Reading `first.name` and `second.name` triggers `Field.__get__`.
  - `User.name` returns the `Field` object itself when accessed through the class.
  - Updating `first.name` does not change `second.name`.
- The second test confirms that assigning an integer to a `Char` field raises `TypeError`.

Running the file executes both tests through Python’s built-in `unittest` framework.
"""


class User(Model):
    _table = "descriptor_test_users"
    name = Char(max_length=50)


class FieldDescriptorTests(unittest.TestCase):
    def test_values_are_stored_per_instance(self):
        first = User(name="Alice")
        second = User(name="Bob")

        self.assertEqual(first.name, "Alice")
        self.assertEqual(second.name, "Bob")
        self.assertIs(User.name, User.__dict__["name"])

        first.name = "Carol"
        self.assertEqual(first.name, "Carol")
        self.assertEqual(second.name, "Bob")

    def test_assignment_validates_field_type(self):
        with self.assertRaises(TypeError):
            User(name=42)

if __name__ == "__main__":
    unittest.main()
