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

def build_form(frame, context, initial_values=None):
    """
    Dynamically builds a form based on column definitions fetched from the configuration.

    Args:
        frame (tk.Frame): The parent frame where form widgets will be added.
        context (str): The context (e.g., "Parts", "Assemblies") to fetch column definitions from config.
        initial_values (dict, optional): Initial values for the form fields.

    Returns:
        dict: A dictionary mapping column names to their respective Tkinter variable objects (e.g., StringVar, IntVar).
    """
    from config.config_data import COLUMN_DEFINITIONS
    from tkinter import Tk, ttk, StringVar
    from core.database_utils import get_processed_column_definitions

    filtered_columns = get_processed_column_definitions(COLUMN_DEFINITIONS.get(context, {}).get("columns", {}))

    # Ensure columns is a dict
    if not isinstance(filtered_columns, dict):
        raise TypeError(f"'columns' for context '{context}' must be a dictionary, got {type(filtered_columns)}")
    
    if not filtered_columns:
        raise ValueError(f"No column definitions found for context '{context}'.")

    entry_widgets = {}
    initial_values = initial_values or {}

    row_counter = 0  # Separate counter for rows to handle skipped fields

    for col_name, col_details in filtered_columns.items():
        
        # Ignore the primary key
        if col_details.get("is_primary_key", False):
            continue

        col_display_name = col_details.get("display_name", col_name)
        col_type = col_details.get("type", "text")
        col_default = initial_values.get(col_name, col_details.get("default"))

        
        # Add label for the field
        label = tk.Label(frame, text=col_display_name)
        label.grid(row=row_counter, column=0, sticky="w", padx=5, pady=5)

        # Determine the widget type and create corresponding input
        if col_type == "options":
            options = col_details.get("options", [])
            entry_var = tk.StringVar(value=col_default or (options[0] if options else ""))
            entry = ttk.Combobox(frame, textvariable=entry_var, values=options, state="readonly")
        elif col_type == "int":
            entry_var = tk.StringVar(value=str(col_default) if col_default is not None else "")
            entry = tk.Entry(frame, textvariable=entry_var)
        elif col_type == "float":
            entry_var = tk.StringVar(value=str(col_default) if col_default is not None else "")
            entry = tk.Entry(frame, textvariable=entry_var, width=30)
        else:  # Default to string type
            entry_var = tk.StringVar(value=col_default or "")
            entry = tk.Entry(frame, textvariable=entry_var, width=30)

        # Add the input widget to the grid
        entry.grid(row=row_counter, column=1, padx=5, pady=5)
        entry_widgets[col_name] = entry_var

        row_counter += 1  # Increment row counter after each widget

    return entry_widgets

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
