# subject to redistribution within new filing structure.

def validate_field(field_name, value, field_type, valid_values=None, default=None):
    """
    Validates a single field based on its type and constraints. If validation fails, assigns a default value if provided.
    Args:
        field_name (str): The name of the field being validated.
        value (any): The value of the field to validate.
        field_type (str): The type of the field ('text', 'int', 'float', 'required').
        valid_values (list, optional): List of acceptable values for the field (e.g., dropdown options).
        default (any, optional): Default value if validation fails.

    Returns:
        any: The validated value or the default.

    Raises:
        ValueError: If validation fails and no default is provided.
    """
    # Check required fields
    if field_type == "required" and not value:
        if default is not None:
            print(f"WARNING: {field_name} is required but missing. Defaulting to {default}.")
            return default
        raise ValueError(f"{field_name} is required.")

    # Check for valid values if specified
    if valid_values and value not in valid_values:
        if default is not None:
            print(f"WARNING: Invalid value for {field_name}: {value}. Defaulting to {default}.")
            return default
        raise ValueError(f"Invalid value for {field_name}: {value}. Expected one of {valid_values}.")

    # Type-specific validation
    if field_type == "int":
        try:
            return int(value)
        except ValueError:
            if default is not None:
                print(f"WARNING: {field_name} must be an integer. Defaulting to {default}.")
                return default
            raise ValueError(f"{field_name} must be an integer.")
    elif field_type == "float":
        try:
            return float(value)
        except ValueError:
            if default is not None:
                print(f"WARNING: {field_name} must be a float. Defaulting to {default}.")
                return default
            raise ValueError(f"{field_name} must be a float.")

    # Validation successful
    return value


def validate_form_data(context, form_data):
    """
    Validates form data before inserting or updating the database.
    Ensures required fields are not empty and follow correct formats.

    Args:
        context (str): The database context (e.g., "Assemblies").
        form_data (dict): The collected form data.

    Returns:
        bool: True if validation passes, False otherwise.

    Raises:
        ValueError: If validation fails.
    """
    from config.config_data import COLUMN_DEFINITIONS

    all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not all_columns:
        raise ValueError(f"No column definitions found for context: {context}")

    print(f"DEBUG: Validating form data for {context}: {form_data}")

    missing_fields = []
    for col_name, col_details in all_columns.items():
        if col_details.get("required", False) and not form_data.get(col_name):
            missing_fields.append(col_name)

    if missing_fields:
        raise ValueError(f"Validation failed: Missing required fields - {missing_fields}")

    print(f"DEBUG: Validation successful for {context}")
    return True


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

def validate_foreign_keys(data, filtered_columns, debug=False):
    """
    Validates foreign key constraints before inserting or updating data.

    Args:
        data (dict): The form data being validated.
        filtered_columns (dict): Column definitions, including foreign key references.

    Raises:
        ValueError: If a foreign key constraint fails.
    """
    from src.core.database_transactions import db_manager  # Ensure db_manager is used

    for col_name, col_details in filtered_columns.items():
        if col_details.get("type") == "foreign_key":
            fk_table = col_details.get("references")  # Name of the referenced table
            fk_column = col_details.get("to", col_name)  # Referenced column (default to the same name)
            fk_value = data.get(col_name)

            # Skip validation if no foreign key value is provided
            if not fk_value:
                continue

            # Debugging: Log foreign key check
            if debug:
                print(f"DEBUG: Validating foreign key: {col_name} -> {fk_table}({fk_column}) with value {fk_value}")

            # Construct query to check if foreign key exists
            fk_query = f"SELECT 1 FROM {fk_table} WHERE {fk_column} = :fk_value"

            try:
                result = db_manager.execute_query(fk_query, {"fk_value": fk_value})

                if not result:
                    raise ValueError(
                        f"The value '{fk_value}' for '{col_name}' does not exist in the referenced table '{fk_table}'."
                    )

            except Exception as e:
                print(f"DEBUG: Foreign key validation error: {e}")
                raise ValueError(
                    f"Foreign key validation failed for column '{col_name}' referencing '{fk_table}({fk_column})': {e}"
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
