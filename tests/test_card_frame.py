import unittest
import os
import tkinter as tk
from ui.ui_components import create_card_frame  # ✅ Ensure correct import path
from core.database_utils import get_assembly_image  # ✅ Ensure function exists
from config.config_data import DEBUG, COLUMN_DEFINITIONS, VIEW_DEFINITIONS

class TestCardFrame(unittest.TestCase):
    """Unit test for create_card_frame function."""

    def setUp(self):
        """Set up a mock Tkinter root window."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main Tk window

        # ✅ Example entity data for testing
        self.test_data = {
            "AssemblyID": 1,
            "AssemblyName": "Test Assembly",
            "ProcurementType": "Make",
            "Quantity": 5,
            "TotalHours": 10
        }

    def test_card_frame_creation(self):
        """Test that the card frame initializes correctly with expected fields."""
        card_frame = create_card_frame(self.root, self.test_data, view_name="card_view")  # ✅ Now inside a method
        self.assertIsNotNone(card_frame)

        # ✅ Get expected fields from VIEW_DEFINITIONS
        expected_fields = VIEW_DEFINITIONS["card_view"]["fields"]

        for field in expected_fields:
            found = any(
                widget for widget in card_frame.winfo_children()
                if isinstance(widget, tk.Label) and str(field) in str(widget.cget("text"))  # ✅ Convert to string
            )
            self.assertTrue(found, f"Field {field} not found in card frame.")

    def tearDown(self):
        """Destroy the Tk root window after tests."""
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()