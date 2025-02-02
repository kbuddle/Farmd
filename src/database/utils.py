import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, StringVar
from src.database.queries import DatabaseQueryExecutor
from src.ui.ui_helpers import UIHelpers

# Define paths
DB_FILE = "src/db/app_data.sqlite"
BACKUP_FOLDER = "src/db/backups/"

# Ensure the backup folder exists
os.makedirs(BACKUP_FOLDER, exist_ok=True)

class DatabaseUtils:
    """ Contains general database-related utility functions. """

    def __init__(self, db_manager):
        """ Accepts a single instance of db_manager to ensure consistency. """
        self.db_executor = DatabaseQueryExecutor(db_manager)

    def get_assembly_image(self, assembly_id):
        """ Retrieves the image path for a given assembly. """
        if not assembly_id:
            return None

        query = """
        SELECT i.ImageFileName
        FROM Assemblies a
        JOIN Images i ON a.AssemImageID = i.ImageID
        WHERE a.AssemblyID = ?
        """
        
        result = self.db_executor.execute_query(query, (assembly_id,))
        return result[0]["ImageFileName"] if result else None  

    def get_entity_details(self, entity_id, entity_type):
        """ Fetches details of an entity (Assembly, Part, or Supplier). """
        query = f"SELECT * FROM {entity_type} WHERE ID = ?"
        result = self.db_executor.execute_query(query, (entity_id,))
        return result[0] if result else {}

    @staticmethod
    def connection_debugger(func):
        """ Decorator for debugging connection-related functions. """
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"DEBUG: {func.__name__} called with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            print(f"DEBUG: {func.__name__} completed.")
            return result
        return wrapper

    def undo_last_action(self, table, fetch_query):
        """ Rolls back the last action and refreshes the table. """
        try:
            if not self.db_executor.transaction_manager.in_transaction:
                messagebox.showerror("Undo Failed", "No active transaction to rollback.")
                return

            self.db_executor.transaction_manager.rollback_transaction()

            rows = self.db_executor.execute_query(fetch_query)

            table.delete(*table.get_children())
            for row in rows:
                table.insert("", "end", values=tuple(row.values()))

            messagebox.showinfo("Undo", "Last action has been undone successfully.")
        except Exception as e:
            messagebox.showerror("Undo Failed", f"Could not undo the last action: {e}")

    @staticmethod
    def backup_database():
        """Creates a timestamped backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.sqlite"
        backup_path = os.path.join(BACKUP_FOLDER, backup_filename)

        try:
            shutil.copy2(DB_FILE, backup_path)
            print(f"✅ Database backup successful: {backup_path}")
        except Exception as e:
            print(f"🚨 Backup failed: {e}")

    @staticmethod
    def prepare_update_params(columns, form_data):
        """
        Prepares a dictionary of parameters for an SQL UPDATE query.

        Args:
            columns (dict): Dictionary containing column metadata.
            form_data (dict): Dictionary containing user input data.

        Returns:
            dict: Dictionary with column names as keys and input values as values.
        """
        params = {}
        for col_name, col_details in columns.items():
            if col_name in form_data:
                value = form_data[col_name]
                if isinstance(value, tk.StringVar):
                    value = value.get()  # ✅ Extract value from Tkinter StringVar if necessary
                params[col_name] = value

        return params
    
    @staticmethod
    def insert_item_in_db(db_query_executor, context, columns, form_data, insert_query, debug=False):
        """
        Inserts a cloned item into the database.

        Args:
            db_query_executor: Database executor instance.
            context (str): Context of the item.
            columns (dict): Column definitions.
            form_data (dict): Data collected from the form.
            insert_query (str): SQL INSERT query.
            debug (bool): Debug flag.

        Raises:
            Exception: If the database insertion fails.
        """
        try:
            params = {
                col: form_data.get(col, None)
                for col in columns.keys()
                if not columns[col].get("is_primary_key", False)
            }

            db_query_executor.execute_non_query(insert_query, params, commit=True)
            UIHelpers.show_info("Success", f"{context} inserted successfully.")

        except Exception as e:
            UIHelpers.show_error("Error", f"Failed to insert {context}: {e}")
            raise