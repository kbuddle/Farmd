import unittest
from unittest.mock import Mock
from src.forms.entity_form import extract_form_data
class MockEntry:
    """ Simulates an entry field in a form. """
    def __init__(self, value):
        self.value = str(value) if value is not None else ""

    def get(self):
        return self.value  # Simulate retrieving user input

class TestExtractFormData(unittest.TestCase):
    """ Unit tests for extract_form_data() """

    def test_default_foreign_key(self):
        """ ✅ Uses default value for foreign key """
        fields = {
            "PartID": MockEntry("201"),
            "PartName": MockEntry("Screw"),
            "DrawingID": MockEntry(""),  # Empty, should be replaced by default
        }
        expected = {"PartID": 201, "PartName": "Screw", "DrawingID": 266}  # Uses default from COLUMN_DEFINITIONS
        result = extract_form_data(fields, "Parts")
        self.assertEqual(result, expected)

    def test_invalid_integer(self):
        """ ❌ Invalid integer should cause a validation error """
        fields = {
            "PartID": MockEntry("abc"),  # Invalid integer
            "PartName": MockEntry("Nut"),
            "PartWeight": MockEntry("1.5"),
        }
        result = extract_form_data(fields, "Parts")
        self.assertIsNone(result)  # Should return None due to error

    def test_valid_input(self):
        """ ✅ Valid input should return correctly typed values """
        fields = {
            "PartID": MockEntry("123"),
            "PartName": MockEntry("Bolt"),
            "PartWeight": MockEntry("2.5"),
        }
        expected = {"PartID": 123, "PartName": "Bolt", "PartWeight": 2.5}
        result = extract_form_data(fields, "Parts")
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
