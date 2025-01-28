def validate_field(field_name, value, field_type, valid_values=None):
    """
    Validates a single field based on its type and constraints.

    Args:
        field_name (str): The name of the field being validated.
        value (any): The value of the field to validate.
        field_type (str): The type of the field ('text', 'int', 'float', 'required').
        valid_values (list, optional): List of acceptable values for the field (e.g., dropdown options).

    Returns:
        bool: True if the field is valid, otherwise raises a ValueError.

    Raises:
        ValueError: If validation fails.
    """
    # Check required fields
    if field_type == "required" and not value:
        raise ValueError(f"{field_name} is required.")
    
    # Check for valid values if specified
    if valid_values and value not in valid_values:
        raise ValueError(f"Invalid value for {field_name}: {value}. Expected one of {valid_values}.")

    # Type-specific validation
    if field_type == "int":
        if not isinstance(value, int):
            try:
                int(value)
            except ValueError:
                raise ValueError(f"{field_name} must be an integer.")
    elif field_type == "float":
        if not isinstance(value, float):
            try:
                float(value)
            except ValueError:
                raise ValueError(f"{field_name} must be a float.")

    # Validation successful
    return True


def validate_form_data(columns, entry_widgets):
    """
    Validates and extracts form data based on column definitions.

    Args:
        columns (list): List of column definitions (dictionaries or strings).
        entry_widgets (dict): Dictionary of entry widgets (Tkinter variables).

    Returns:
        dict: Validated form data.

    Raises:
        ValueError: If validation fails for any field.
    """
    form_data = {}

    for column in columns:
        # Handle both dictionary and string formats for columns
        if isinstance(column, dict):
            col_name = column["name"]
            col_type = column.get("type", "text")
        elif isinstance(column, str):
            col_name = column
            col_type = "text"  # Default to text if type is not specified
        else:
            raise ValueError(f"Invalid column format: {column}")

        # Get the entry widget's value
        entry_var = entry_widgets.get(col_name)
        if not entry_var:
            continue  # Skip columns without widgets

        value = entry_var.get()

        # Perform validation based on type (e.g., required fields, numeric values)
        if col_type in ["int", "float"] and value == "":
            raise ValueError(f"{col_name} cannot be empty.")
        if col_type == "int":
            value = int(value)
        elif col_type == "float":
            value = float(value)

        form_data[col_name] = value

    return form_data

def validate_table_selection(table, context):
    """
    Validates that a selection has been made in the table.

    Args:
        table (ttk.Treeview): The Treeview widget to validate.
        context (str): Context of the selection (e.g., "Parts", "Assemblies").

    Returns:
        list: Selected values from the table.

    Raises:
        ValueError: If no selection is made.
    """
    selected_item = table.selection()
    if not selected_item:
        raise ValueError(f"Please select a {context} to proceed.")
    return table.item(selected_item, "values")

def validate_foreign_keys(data, filtered_columns, connection):
    for col_name, col_details in filtered_columns.items():
        if col_details.get("type") == "foreign_key":
            fk_table = col_details.get("references")  # Name of the referenced table
            fk_column = col_details.get("to", col_name)  # Referenced column (default to the same name)
            fk_value = data.get(col_name)

            if fk_value:
                fk_query = f"SELECT 1 FROM {fk_table} WHERE {fk_column} = ?"
                result = connection.execute(fk_query, (fk_value,)).fetchone()
                if not result:
                    raise ValueError(
                        f"The value '{fk_value}' for '{col_name}' does not exist in the referenced table '{fk_table}'."
                    )

def validate_contexts(contexts):
    """
    Validates that the contexts object is a dictionary.

    Args:
        contexts (Any): The contexts object to validate.

    Raises:
        TypeError: If contexts is not a dictionary.
    """
    if not isinstance(contexts, dict):
        raise TypeError(f"'contexts' must be a dictionary, got {type(contexts)}")
