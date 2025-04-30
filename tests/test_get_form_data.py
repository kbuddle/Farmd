import unittest
import tkinter as tk
from src.forms.entity_form import EntityForm
from config.config_data import COLUMN_DEFINITIONS

# ✅ Lightweight subclass that disables unnecessary dependencies
class TestableEntityForm(EntityForm):
    def __init__(self, parent, entity_name, *args, **kwargs):
        """ ✅ Assign valid tree_view_def and detail_view_def before calling super().__init__() """
        kwargs["tree_view_def"] = {
            "tree": {
                "columns": ["PartID", "PartName", "PartWeight"],
                "headings": {"PartID": "ID", "PartName": "Name", "PartWeight": "Weight"}
            }
        }
        kwargs["detail_view_def"] = {  # ✅ Prevent KeyError in populate_detail_frame()
            "detail_frame": {"text": "Part Details"},
            "fields": {}  # ✅ Ensure 'fields' exists
        }
        super().__init__(parent, entity_name, *args, **kwargs)
        self.fields = {}  # ✅ Manually set fields for testing
        self.entity_tree = None  # ✅ Avoid UI dependency

    def populate_tree(self):
        """ ✅ Disable database interaction """
        pass

class MockEntry:
    """ Simulates an entry field in a form. """
    def __init__(self, value):
        self.value = str(value) if value is not None else ""

    def get(self):
        return self.value  # Simulate retrieving user input

class TestEntityForm(unittest.TestCase):
    """ Unit tests for get_form_data() inside EntityForm """

    def setUp(self):
        """ ✅ Use a real Tkinter root window but avoid full UI setup """
        self.root = tk.Tk()
        self.root.withdraw()

        self.entity_form = TestableEntityForm(
            parent=self.root,
            entity_name="Parts",
            data_manager={},  # ✅ No need for full DatabaseService
            main_app={}
        )

    def tearDown(self):
        """ ✅ Destroy the Tkinter root after each test """
        self.root.destroy()

    def test_default_foreign_key(self):
        """ ✅ Uses default value for foreign key """
        self.entity_form.fields = {
            "PartID": MockEntry("201"),
            "PartName": MockEntry("Screw"),
            "DrawingID": MockEntry(""),
        }
        expected = {"PartID": 201, "PartName": "Screw", "DrawingID": 266}  # Uses default from COLUMN_DEFINITIONS
        result = self.entity_form.get_form_data()
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
