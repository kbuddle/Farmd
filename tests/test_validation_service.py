import unittest
from src.services.validation_service import ValidationService

class MockEntry:
    """ Simulates an entry field in a form. """
    def __init__(self, value):
        self.value = str(value) if value is not None else ""

    def get(self):
        return self.value  # Simulate retrieving user input

import unittest
from src.services.validation_service import ValidationService

class TestValidationService(unittest.TestCase):
    def setUp(self):
        column_definitions = {
            "PartID": {"type": "int", "required": True},
            "PartName": {"type": "str", "required": True},
            "PartWeight": {"type": "float", "required": False},
            "DrawingID": {"type": "int", "required": False}
        }
        self.validation_service = ValidationService(column_definitions)

    def test_invalid_float(self):
        with self.assertRaises(ValueError) as context:
            self.validation_service.validate_field("PartWeight", "xyz", "float")
        self.assertIn("❌ PartWeight must be a valid float.", str(context.exception))

    def test_invalid_integer(self):
        with self.assertRaises(ValueError) as context:
            self.validation_service.validate_field("PartID", "abc", "int")
        self.assertIn("❌ PartID must be a valid int.", str(context.exception))

    def test_missing_required_field(self):
        with self.assertRaises(ValueError) as context:
            self.validation_service.validate_field("PartName", "", "str", required=True)
        self.assertIn("❌ PartName is required.", str(context.exception))

    def test_valid_integer(self):
        result = self.validation_service.validate_field("PartID", "123", "int")
        self.assertEqual(result, 123)

    def test_valid_float(self):
        result = self.validation_service.validate_field("PartWeight", "2.5", "float")
        self.assertEqual(result, 2.5)

if __name__ == "__main__":
    unittest.main()
