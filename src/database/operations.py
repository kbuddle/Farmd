import tkinter as tk
from tkinter import messagebox
from src.database.queries import DatabaseQueryExecutor
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from config.config_data import COLUMN_DEFINITIONS

class DatabaseOperations:
    """ Handles add, update, delete, and clone operations on database records. """
    
    import tkinter as tk
from src.database.queries import DatabaseQueryExecutor
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from config.config_data import COLUMN_DEFINITIONS
from src.ui.ui_helpers import UIHelpers  # ✅ Import UI Helpers
from src.database.utils import DatabaseUtils  # ✅ Import DatabaseUtils


class DatabaseOperations:
    """ Handles add, update, delete, and clone operations on database records. """
    
    def __init__(self, db_manager):
        """ Accepts a single instance of db_manager to ensure consistency. """
        self.db_manager = db_manager
        self.db_query_executor = DatabaseQueryExecutor(db_manager)

    def add_item(self, context_name, table, insert_query, fetch_query, debug=False):
        """ Opens a form to add a new record. """
        columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
        editable_columns = {col: details for col, details in columns.items() if not details.get("admin", False)}
        form_window, entry_widgets = build_form(context_name, editable_columns, initial_data={})

        def save_item():
            try:
                form_data = {col: var.get() for col, var in entry_widgets.items()}
                self.db_query_executor.execute_non_query(insert_query, form_data, commit=True)
                UIHelpers.show_info("Success", f"{context_name} added successfully.")
                form_window.destroy()
            except Exception as e:
                UIHelpers.show_error("Error", f"Failed to add {context_name}: {e}")

        tk.Button(form_window, text="Save", command=save_item, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
        form_window.mainloop()

    def edit_item(self, context, table, fetch_query, update_query, debug=False):
        """ Opens a window to edit an existing item. """
        from tkinter import ttk, Button
        
        all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        if not all_columns:
            UIHelpers.show_error("Configuration Error", f"No column definitions found for {context}.")
            return
        
        editable_columns = {col: details for col, details in all_columns.items() if not details.get("admin", False)}
        selected_item = table.selection()
        if not selected_item:
            UIHelpers.show_error("Selection Error", "No item selected for editing.")
            return
        
        initial_data = {col: table.set(selected_item, col) for col in editable_columns.keys()}
        form_window, entry_widgets = build_form(context, editable_columns, initial_data)
        
        def save_changes():
            try:
                form_data = {col: var.get() for col, var in entry_widgets.items()}
                validate_form_data(context, form_data)
                self.db_query_executor.execute_non_query(update_query, form_data, commit=True)
                UIHelpers.show_info("Success", f"{context} updated successfully.")
                form_window.destroy()
            except Exception as e:
                UIHelpers.show_error("Error", f"Failed to save changes: {e}")
        
        tk.Button(form_window, text="Save", command=save_changes, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")

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