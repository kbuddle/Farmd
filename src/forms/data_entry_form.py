# subject to redistribution within new filing structure.

import tkinter as tk
from config.config_data import COLUMN_DEFINITIONS
from tkinter import Tk, ttk, StringVar, messagebox



def gather_form_data(context, entry_widgets):
    """
    Collects and validates data from the form.

    Args:
        context (str): The context of the form (e.g., "Parts").
        entry_widgets (dict): A dictionary mapping column names to Tkinter variables.

    Returns:
        dict: Validated form data.

    Raises:
        ValueError: If validation fails for any field.
    """
    from config.config_data import COLUMN_DEFINITIONS

    columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not columns:
        raise ValueError(f"No column definitions found for context '{context}'.")

    form_data = {}

    for col_name, col_details in columns.items():
        col_type = col_details.get("type", "text")  # Default type is "text"
        is_required = col_details.get("required", False)  # Optional "required" flag
        valid_options = col_details.get("options", [])  # Options for "options" type fields

        entry_var = entry_widgets.get(col_name)
        if entry_var is None:
            continue  # Skip fields not present in the form

        value = entry_var.get().strip()

        # Skip primary keys (not editable)
        if col_details.get("is_primary_key", False):
            continue

        # Handle required fields
        if is_required and not value:
            raise ValueError(f"The field '{col_details.get('display_name', col_name)}' is required but was left empty.")

        # Convert and validate data based on type
        if not value:  # Allow nullable fields
            form_data[col_name] = None
        elif col_type == "int":
            try:
                form_data[col_name] = int(value)
            except ValueError:
                raise ValueError(f"Invalid integer value for '{col_details.get('display_name', col_name)}': {value}")
        elif col_type == "float":
            try:
                form_data[col_name] = float(value)
            except ValueError:
                raise ValueError(f"Invalid float value for '{col_details.get('display_name', col_name)}': {value}")
        elif col_type == "options":
            if value not in valid_options:
                raise ValueError(f"Invalid option for '{col_details.get('display_name', col_name)}': {value}. Valid options are {valid_options}.")
            form_data[col_name] = value
        else:  # Default to text
            form_data[col_name] = value

    return form_data

def build_form(context, columns, initial_data=None, readonly_fields=None):
    """
    Builds a dynamic Tkinter form for data entry or editing.
    
    Supports:
    - Initial values
    - Readonly fields (e.g., primary keys)
    
    Args:
        context (str): The context of the form (e.g., "Assemblies").
        columns (dict): Column definitions.
        initial_data (dict, optional): Initial values for the form fields.
        readonly_fields (list, optional): List of field names that should be readonly.

    Returns:
        tuple: (Tkinter Toplevel window, dictionary of entry widgets)
    """

    from src.ui.ui_helpers import center_window_vertically
    
    form_window = tk.Toplevel()
    form_window.title(f"{context} Entry Form")
    center_window_vertically(form_window, 600, 750)
    entry_widgets = {}

    # Ensure initial_data is a dictionary to avoid NoneType errors
    if initial_data is None:
        initial_data = {}
        
    for i, (col_name, col_details) in enumerate(columns.items()):
        label = tk.Label(form_window, text=col_details.get("display_name", col_name))
        label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

        entry_var = tk.StringVar(value=initial_data.get(col_name, ""))
        entry = tk.Entry(form_window, textvariable=entry_var)

        # Make fields readonly if specified
        if readonly_fields and col_name in readonly_fields:
            entry.config(state="readonly")

        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entry_widgets[col_name] = entry_var

    return form_window, entry_widgets

def populate_form_for_edit(data, column_definitions):
    """
    Populates the data entry form for editing or cloning.

    Args:
        data (dict): The data to populate the form with.
        column_definitions (dict): Column definitions for the context.

    Returns:
        dict: Processed form data, including hidden/readonly fields.
    """
    form_data = {}

    for column, value in data.items():
        column_metadata = column_definitions.get(column, {})
        is_primary_key = column_metadata.get("is_primary_key", False)
        allow_null = column_metadata.get("allow_null", True)

        # Replace None with NULL or default empty value based on column metadata
        processed_value = "NULL" if value is None and allow_null else value or ""

        # Handle primary keys separately
        if is_primary_key:
            form_data[column] = processed_value
            hide_field_in_ui(column, processed_value)  # Hypothetical function for hiding fields
        else:
            form_data[column] = processed_value
            add_field_to_ui(column, processed_value)  # Hypothetical function for adding visible fields

    return form_data

def prepare_form_data(treeview, columns):
    """
    Prepares form data for an edit operation by retrieving the selected item from the Treeview.

    Args:
        treeview (ttk.Treeview): The Treeview containing the data.
        columns (dict): Dictionary containing column definitions.

    Returns:
        dict: A dictionary containing form data for editing.
    """
    selected_item = treeview.selection()  # Get the selected row
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected for editing.")
        return None

    # Retrieve item values from the Treeview
    item_values = treeview.item(selected_item, "values")
    form_data = {}

    # Populate form_data, including the primary key
    for index, (col_name, col_details) in enumerate(columns.items()):
        if col_details.get("is_primary_key", False):
            # Add the primary key to form_data
            form_data[col_name] = item_values[index]
        else:
            # Assume the rest of the data is tied to a Tkinter StringVar
            form_data[col_name] = tk.StringVar(value=item_values[index])

    print(f"DEBUG: Prepared form_data for editing: {form_data}")
    return form_data
