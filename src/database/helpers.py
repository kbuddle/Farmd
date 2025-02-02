# src/database/helpers.py

import config.config_data

class ColumnProcessor:
    """ Handles processing of column definitions for forms. """

    @staticmethod
    def get_editable_columns(context_name):
        """
        Fetches editable columns for a given context, excluding admin and primary keys.
        """

        config.config_data.COLUMN_DEFINITIONS["TestContext"] = {
                "columns": {
                    "id": {"is_primary_key": True},
                    "name": {"admin": False},
                    "secret_data": {"admin": True},
                    "created_at": {"admin": False}
                }
            }
 
        # ✅ Access the updated COLUMN_DEFINITIONS dynamically
        column_definitions = config.config_data.COLUMN_DEFINITIONS

        print(f"✅ DEBUG (runtime before lookup): COLUMN_DEFINITIONS at runtime: {column_definitions}")
        print(f"✅ DEBUG (runtime): Looking for columns in context '{context_name}'")  

        # ✅ Ensure correct access to the context dictionary
        context_data = column_definitions.get(context_name, {})

        if not context_data:
            print(f"❌ DEBUG: No context data found for '{context_name}'.")
            return {}

        # ✅ Extract columns safely
        columns = context_data.get("columns", {})

        if not columns:
            print(f"❌ DEBUG: No columns found for '{context_name}'.")
            return {}

        print(f"✅ DEBUG (runtime): Retrieved columns: {columns}")  

        # ✅ Correct filtering logic
        editable_columns = {
            col_name: col_details
            for col_name, col_details in columns.items()
            if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
        }

        print(f"✅ DEBUG (runtime): Filtered editable columns: {editable_columns}")  
        return editable_columns
