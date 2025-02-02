import tkinter as tk
from tkinter import messagebox
from src.database.queries import DatabaseQueryExecutor
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from config.config_data import COLUMN_DEFINITIONS
from src.database.helpers import ColumnProcessor
from src.database.queries import DatabaseQueryExecutor
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from config.config_data import COLUMN_DEFINITIONS
from src.ui.ui_helpers import UIHelpers  # ✅ Import UI Helpers
from src.database.utils import DatabaseUtils  # ✅ Import DatabaseUtils
from src.ui.form_window import FormWindow

class DatabaseOperations:
    """ Handles add, update, delete, and clone operations on database records. """
    
    



class DatabaseOperations:
    """ Handles add, update, delete, and clone operations on database records. """
    
    def __init__(self, db_manager):
        """ Accepts a single instance of db_manager to ensure consistency. """
        self.db_manager = db_manager
        self.db_query_executor = DatabaseQueryExecutor(db_manager)

    def add_item(self, context_name, table, insert_query, fetch_query, debug=False):
        """ Opens a form to add a new record. """

        # Get editable columns via ColumnProcessor
        editable_columns = ColumnProcessor.get_editable_columns(context_name)

        if not editable_columns:
            UIHelpers.show_error("Configuration Error", f"No column definitions found for '{context_name}'.")
            return

        def save_item(form_data):
            """ Saves the new record to the database. """
            try:
                self.db_query_executor.execute_non_query(insert_query, form_data, commit=True)
                UIHelpers.show_info("Success", f"{context_name} added successfully.")
            except Exception as e:
                UIHelpers.show_error("Error", f"Failed to add {context_name}: {e}")

        # Create the UI form with pre-filled values
        FormWindow(title=f"Add {context_name}", fields=editable_columns, on_save_callback=save_item)

    def edit_item(self, context_name, table, fetch_query, update_query, debug=False):
        """ Opens a form to edit an existing record. """

        # Get editable columns via ColumnProcessor
        editable_columns = ColumnProcessor.get_editable_columns(context_name)

        if not editable_columns:
            UIHelpers.show_error("Configuration Error", f"No column definitions found for '{context_name}'.")
            return

        # Ensure an item is selected before proceeding
        selected_item = table.selection()
        if not selected_item:
            UIHelpers.show_error("Selection Error", "No item selected for editing.")
            return

        # Extract selected item data
        initial_data = {col: table.set(selected_item, col) for col in editable_columns.keys()}

        def save_changes(form_data):
            """ Saves the modified record to the database. """
            try:
                validate_form_data(context_name, form_data)
                self.db_query_executor.execute_non_query(update_query, form_data, commit=True)
                UIHelpers.show_info("Success", f"{context_name} updated successfully.")

                # Refresh the table with updated data
                rows = self.db_query_executor.execute_query(fetch_query)
                table.delete(*table.get_children())
                for row in rows:
                    table.insert("", "end", values=tuple(row.values()))

            except Exception as e:
                UIHelpers.show_error("Error", f"Failed to save changes: {e}")

        # Create the UI form with pre-filled values
        FormWindow(title=f"Edit {context_name}", fields=editable_columns, on_save_callback=save_changes, initial_data=initial_data)

    def delete_item(self, context_name, table, fetch_query, delete_query):
        """ Deletes a selected item from the database. """
        selected_item = table.selection()
        if not selected_item:
            UIHelpers.show_error("Selection Error", "No item selected for deletion.")
            return
        
        confirm = UIHelpers.ask_confirmation("Confirm Deletion", f"Are you sure you want to delete this {context_name}?")
        if not confirm:
            return
        
        self.db_query_executor.execute_non_query(delete_query, {"ID": selected_item[0]}, commit=True)
        UIHelpers.show_info("Success", f"{context_name} deleted successfully.")

    def update_item_in_db(self, context, columns, form_data, update_query, debug=False):
        """ Updates an existing database record. """
        try:
            primary_key = next((col for col, details in columns.items() if details.get("is_primary_key", False)), None)
            if not primary_key:
                raise ValueError(f"No primary key defined for context: {context}")

            params = DatabaseUtils.prepare_update_params(columns, form_data)  # ✅ Now using DatabaseUtils
            params["primary_key_value"] = form_data.get(primary_key)

            self.db_query_executor.execute_non_query(update_query, params)

        except Exception as e:
            UIHelpers.show_error("Error", f"Failed to update {context}: {e}")
            raise
    
    def insert_item(self, context, columns, form_data, insert_query, debug=False):
        """ Calls the utility function to insert an item into the database. """
        DatabaseUtils.insert_item_in_db(self.db_query_executor, context, columns, form_data, insert_query, debug)

    def clone_item(self, context_name, table, fetch_query, insert_query, debug=False):
        """ Clones an existing item, allows editing, and refreshes the table upon success. """

        # Get editable columns via ColumnProcessor
        editable_columns = ColumnProcessor.get_editable_columns(context_name)

        if not editable_columns:
            UIHelpers.show_error("Configuration Error", f"No column definitions found for '{context_name}'.")
            return

        # Ensure an item is selected before proceeding
        selected_item = table.selection()
        if not selected_item:
            UIHelpers.show_error("Selection Error", "No item selected for cloning.")
            return

        # Extract selected item data for cloning
        original_data = {col: table.set(selected_item, col) for col in editable_columns.keys()}

        def save_clone(form_data):
            """ Saves the cloned record to the database. """
            try:
                if debug:
                    print(f"DEBUG: Form data for cloned item: {form_data}")

                # Validate form data before inserting
                validate_form_data(context_name, form_data)

                # Execute the insert query
                self.db_query_executor.execute_non_query(insert_query, form_data, commit=True)

                # Refresh the table with updated data
                rows = self.db_query_executor.execute_query(fetch_query)
                table.delete(*table.get_children())
                for row in rows:
                    table.insert("", "end", values=tuple(row.values()))

                UIHelpers.show_info("Success", f"{context_name} cloned successfully.")

            except Exception as e:
                UIHelpers.show_error("Error", f"Failed to clone {context_name}: {e}")
                if debug:
                    print(f"DEBUG: Cloning error: {e}")

        # Create the UI form with pre-filled values
        FormWindow(title=f"Clone {context_name}", fields=editable_columns, on_save_callback=save_clone, initial_data=original_data)
