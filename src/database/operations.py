import tkinter as tk
from tkinter import messagebox
from src.database.queries import DatabaseQueryExecutor
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from config.config_data import COLUMN_DEFINITIONS

class DatabaseOperations:
    """ Handles add, update, delete, and clone operations on database records. """
    
    def __init__(self, db_manager):
        """ Accepts a single instance of db_manager to ensure consistency. """
        self.db_manager = db_manager
        self.db_query_executor = DatabaseQueryExecutor(db_manager)

    def add_item(context_name, table, insert_query, fetch_query, debug=False):
        """ Opens a form to add a new record. """
        
        columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
        result = self.db_query_executor.execute_non_query(insert_query, columns)

        editable_columns = {col: details for col, details in columns.items() if not details.get("admin", False)}

        form_window, entry_widgets = build_form(context_name, editable_columns, initial_data={})

        def save_item():
            try:
                form_data = {col: var.get() for col, var in entry_widgets.items()}
                db_query_executor.execute_non_query(insert_query, form_data, commit=True) #FLAG
                messagebox.showinfo("Success", f"{context_name} added successfully.")
                form_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {context_name}: {e}")

        tk.Button(form_window, text="Save", command=save_item, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
        form_window.mainloop()
    
    def edit_item(context, table, fetch_query, update_query, debug=False):
        """
        Opens a window to edit an existing item and refreshes the table upon success.
        """
        from tkinter import ttk, Button

        all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        if not all_columns:
            messagebox.showerror("Configuration Error", f"No column definitions found for context '{context}'.")
            return

        if debug:
            print(f"DEBUG: All columns for edit_item: {all_columns}")

        editable_columns = {col: details for col, details in all_columns.items() if not details.get("admin", False)}

        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No item selected for editing.")
            return

        initial_data = {col: table.set(selected_item, col) for col in editable_columns.keys()}
        form_window, entry_widgets = build_form(context, editable_columns, initial_data)

        def save_changes():
            try:
                form_data = {col: var.get() for col, var in entry_widgets.items()}
                if debug:
                    print(f"DEBUG: Form data collected for {context}: {form_data}")

                validate_form_data(context, form_data)

                self.db_query_executor.execute_non_query(update_query, form_data, commit=False) #FLAG

                confirm = messagebox.askyesno("Confirm Save", "Do you want to save these changes?")
                if confirm:
                    self.db_query_executor.commit_transaction() #FLAG
                    messagebox.showinfo("Success", f"{context} updated successfully.")

                rows = self.db_query_executor.execute_query(fetch_query)

                table.delete(*table.get_children())
                for row in rows:
                    table.insert("", "end", values=tuple(row.values()))

                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save changes: {e}")
                print(f"DEBUG: Error while saving changes: {e}")

        tk.Button(form_window, text="Save", command=save_changes, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
    
    def clone_item(context_name, table, fetch_query, insert_query, debug=False):
        """
        Clones an existing item, allows editing, and refreshes the table upon success.
        """
        
        all_columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
        if not all_columns:
            messagebox.showerror("Configuration Error", f"No column definitions found for context '{context_name}'.")
            return

        if debug:
            print(f"DEBUG: All columns for clone_item: {all_columns}")

        editable_columns = {
            col_name: col_details
            for col_name, col_details in all_columns.items()
            if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
        }

        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No item selected for cloning.")
            return

        original_data = {col_name: table.set(selected_item, col_name) for col_name in editable_columns.keys()}
        form_window, entry_widgets = build_form(context_name, editable_columns, original_data)

        def save_clone():
            try:
                form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
                if debug:
                    print(f"DEBUG: Form data for cloned item: {form_data}")

                if not validate_form_data(context_name, form_data):
                    raise ValueError(f"Validation failed for cloned form data: {form_data}")

               
                self.db_query_executor.execute_non_query(insert_query, form_data, commit=True)  #FLAG

                rows = self.db_query_executor.execute_query(fetch_query) #FLAG

                table.delete(*table.get_children())
                for row in rows:
                    table.insert("", "end", values=tuple(row.values()))

                messagebox.showinfo("Success", f"{context_name} cloned successfully.")
                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to clone the {context_name}: {e}")
                if debug:
                    print(f"DEBUG: Cloning error: {e}")

        tk.Button(form_window, text="Save", command=save_clone, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")

    def delete_item(context_name, table, fetch_query, delete_query):
        """ Deletes a selected item from the database. """
        
        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No item selected for deletion.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this {context_name}?")
        if not confirm:
            return

        self.db_query_executor.execute_non_query(delete_query, {"ID": selected_item[0]}, commit=True)  #FLAG
        messagebox.showinfo("Success", f"{context_name} deleted successfully.")

    def update_item_in_db(context, columns, form_data, update_query, debug=False):
        """
        Updates a specific item in the database using the provided form data.
        """
        
        try:
            primary_key = next(
                (col_name for col_name, col_details in columns.items() if col_details.get("is_primary_key", False)),
                None
            )
            if not primary_key:
                raise ValueError(f"No primary key defined for context: {context}")

            if primary_key not in form_data:
                raise ValueError(f"Primary key '{primary_key}' is missing in the form data.")

            params = {col_name: form_data.get(col_name, None) for col_name in columns.keys()}
            params["primary_key_value"] = form_data.get(primary_key)

            if "WHERE" not in update_query.upper():
                update_query += f" WHERE {primary_key} = :primary_key_value"

            self.db_query_executor.execute_non_query(update_query, params)  #FLAG

            if debug:
                print(f"DEBUG: Update successful for context: {context}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update {context}: {e}")
            raise

    def insert_item_in_db(context, columns, form_data, insert_query, debug=False):
        """
        Inserts a cloned item into the database.
        """
        try:
            params = {
                col_name: form_data.get(col_name, None)
                for col_name in columns.keys()
                if not columns[col_name].get("is_primary_key", False)
            }

            if debug:
                print(f"DEBUG: Insert parameters for {context}: {params}")

              
            self.db_query_executor.execute_non_query(insert_query, params)  #FLAG

            if debug:
                print(f"DEBUG: Insert successful for context: {context}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert {context}: {e}")
            raise

    @staticmethod
    def prepare_update_params(columns, form_data):
        """
        Prepares a dictionary of parameters for an SQL UPDATE query.
        """
        params = {}
        for col_name, col_details in columns.items():
            if col_name in form_data:
                value = form_data[col_name]
                if isinstance(value, tk.StringVar):
                    value = value.get()
                params[col_name] = value

        return params