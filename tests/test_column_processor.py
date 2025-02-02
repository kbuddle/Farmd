import unittest
import sys
import os
import importlib

# Ensure the project root is in the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🔹 Import and overwrite COLUMN_DEFINITIONS for testing
import config.config_data

config.config_data.COLUMN_DEFINITIONS = {
    "TestContext": {
        "columns": {
            "id": {"is_primary_key": True},
            "name": {"admin": False},
            "secret_data": {"admin": True},
            "created_at": {"admin": False}
        }
    }
}

print(f"DEBUG: COLUMN_DEFINITIONS at test level: {config.config_data.COLUMN_DEFINITIONS}")

# 🔹 Reload the config module to apply the changes
importlib.reload(config.config_data)

print(f"DEBUG: COLUMN_DEFINITIONS at test level after reload: {config.config_data.COLUMN_DEFINITIONS}")

# ✅ Import ColumnProcessor after COLUMN_DEFINITIONS is modified
from src.database.helpers import ColumnProcessor

class TestColumnProcessor(unittest.TestCase):
    
    def test_get_editable_columns(self):
        """ Test that ColumnProcessor correctly filters editable columns. """
        
        # 🔹 Debug print to verify COLUMN_DEFINITIONS
        print(f"DEBUG (test runtime): COLUMN_DEFINITIONS: {config.config_data.COLUMN_DEFINITIONS}")

        expected_columns = {
            "name": {"admin": False},
            "created_at": {"admin": False}
        }

        # 🔹 Debug print before calling the method
        print(f"DEBUG: Calling ColumnProcessor.get_editable_columns('TestContext')")

        result = ColumnProcessor.get_editable_columns("TestContext")

        # 🔹 Debug print after getting the result
        print(f"DEBUG: Result from ColumnProcessor: {result}")

        self.assertEqual(result, expected_columns, "Filtered columns do not match expected output.")

    def test_get_editable_columns_real_context(self):
        """ Test that ColumnProcessor correctly filters editable columns for 'Assemblies'. """

        expected_columns = {
            "AssemName": {"display_name": "Name", "width": 200, "type": "string"},
            "ParentAssemblyID": {"display_name": "Parent Assembly", "width": 100, "type": "int", "default": 40},
            "AssemImageRef": {"display_name": "Image Reference", "width": 150, "type": "string"},
            "AssemDwgID": {"display_name": "Drawing ID", "width": 200, "type": "int", "default": 266},
            "AssemCost": {"display_name": "Cost", "width": 80, "type": "numeric"},
            "AssemWeight": {"display_name": "Weight", "width": 80, "type": "numeric"},
            "AssemHoursParts": {"display_name": "Hours (Parts)", "width": 100, "type": "numeric", "default": 0},
            "AssemHoursAssembly": {"display_name": "Hours (Assembly)", "width": 100, "type": "numeric", "default": 0},
            "AssemFocus": {"display_name": "Focus", "width": 100, "type": "string", "default": "Medium"},
            "AssemCostFlag": {"display_name": "Cost Flag", "width": 80, "type": "int", "default": 0},
            "AssemWeightFlag": {"display_name": "Weight Flag", "width": 80, "type": "int", "default": 0},
            "AssemStatus": {"display_name": "Status", "width": 100, "type": "string", "default": "Prelim"},
            "AssemNotes": {"display_name": "Notes", "width": 200, "type": "string"},
            "ProcurementType": {"display_name": "Procurement Type", "width": 100, "type": "string", "default": "Purchase"}
        }

        result = ColumnProcessor.get_editable_columns("Assemblies")

        print(f"DEBUG: Result from ColumnProcessor for 'Assemblies': {result}")  # Debug print
        self.assertEqual(result, expected_columns, "Filtered columns for 'Assemblies' do not match expected output.")

    def test_get_editable_columns_parts(self):
        """ Test that ColumnProcessor correctly filters editable columns for 'Parts'. """

        expected_columns = {
            "PartName": {"display_name": "Name", "width": 200, "type": "string", "parts": True},
            "Model": {"display_name": "Model", "width": 100, "type": "string", "parts": True},
            "Make": {"display_name": "Make", "width": 100, "type": "string", "parts": True},
            "Dimensions": {"display_name": "Dimensions", "width": 150, "type": "string", "parts": True},
            "Notes": {"display_name": "Notes", "width": 100, "type": "string", "parts": True},
            "Manufacturer": {"display_name": "Manufacturer", "width": 100, "type": "string", "parts": True},
            "ImageRef": {"display_name": "ImageRef", "width": 100, "type": "string"},
            "DrawingID": {"display_name": "DrawingID", "width": 100, "type": "int", "foreign_key": True, "default": 266},
            "ManPartNum": {"display_name": "ManPartNum", "width": 100, "type": "string", "parts": True},
            "ProcurementType": {"display_name": "ProcurementType", "width": 100, "type": "string", "default": "Purchase"},
            "PartWeight": {"display_name": "Weight", "width": 80, "type": "float", "default": 0},
            "PartMaterial": {"display_name": "Material", "width": 100, "type": "string"},
        }

        result = ColumnProcessor.get_editable_columns("Parts")

        print(f"DEBUG: Result from ColumnProcessor for 'Parts': {result}")  # Debug print
        self.assertEqual(result, expected_columns, "Filtered columns for 'Parts' do not match expected output.")

# Run the tests
if __name__ == '__main__':
    unittest.main()
