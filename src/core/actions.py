#actions.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.shared_utils import populate_table
from src.forms.data_entry_form import build_form
from src.forms.validation import validate_form_data
from src.core.database_transactions import db_manager
from src.core.config_utils import get_primary_key
from config.config_data import COLUMN_DEFINITIONS

def add_item(context_name, table=None, insert_query=None, fetch_query=None, post_insert_callback=None, debug=False):
    """
    Opens a window to add a new item and refreshes the table upon success.
    """
    columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
    if not columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context_name}'.")
        return
    
    editable_columns = {
        col_name: col_details
        for col_name, col_details in columns.items()
        if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
    }

    form_window, entry_widgets = build_form(context_name, editable_columns, initial_data={})

    def save_item():
        try:
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            db_manager.execute_non_query(insert_query, form_data, commit=False)
            confirm = messagebox.askyesno("Confirm Save", "Do you want to save this item permanently?")
            if confirm:
                db_manager.commit_transaction()

            if table and fetch_query:
                rows = db_manager.execute_query(fetch_query)
                table.delete(*table.get_children())
                for row in rows:
                    table.insert("", "end", values=tuple(row.values()))

            messagebox.showinfo("Success", f"New {context_name} added successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add new {context_name}: {e}")

    tk.Button(form_window, text="Save", command=save_item, bg="green", fg="white").grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")
    tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white").grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")

    form_window.mainloop()

