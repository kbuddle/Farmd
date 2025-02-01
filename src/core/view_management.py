# subject to redistribution within new filing structure.

def get_processed_column_definitions(column_definitions, exclude_hidden=True, debug=False):
    """
    Processes column definitions, optionally filtering out hidden or admin-only columns.

    Args:
        column_definitions (dict): Dictionary of column definitions.
        exclude_hidden (bool): Whether to exclude columns flagged as hidden.

    Returns:
        list: A list of column names, optionally excluding hidden or admin-only columns.
    """
    if debug:
        print(f"get_processed_column_definitions called with:")
        print(f"  column_definitions: {column_definitions} (type: {type(column_definitions)})")
        print(f"  exclude_hidden: {exclude_hidden}")
    
    if not isinstance(column_definitions, dict):
        raise TypeError(f"Expected 'column_definitions' to be a dictionary, got {type(column_definitions).__name__}. Value: {column_definitions}")
    
    if debug:
        print(f"Processing column definitions: {column_definitions}")
    processed_columns= {
        col: details
        for col, details in column_definitions.items()
        if details.get("is_primary_key", False) or not (exclude_hidden and details.get("admin", False))
    }
    
    return processed_columns


def get_processed_columns(context_name, debug=True):
    """
    Retrieves processed column definitions for a given context.

    Args:
        context_name (str): The name of the context (e.g., "Assemblies", "Parts").

    Returns:
        list: A list of dictionaries containing column names and properties.
    """
    from config.config_data import COLUMN_DEFINITIONS

    if debug:
        print(f"get_processed_column_definitions called with:")
        print(f"  column_definitions: {context_name}")
      
    # Retrieve column definitions from configuration
    context_data = COLUMN_DEFINITIONS.get(context_name, {})

    # Debug: Print retrieved structure
    print(f"\n🔍 DEBUG: get_processed_columns() retrieved for {context_name}: {context_data}\n")

    if not context_data:
        raise ValueError(f"ERROR: No column definitions found for '{context_name}'.")

    # ✅ Convert dictionary-based columns into a structured list of dictionaries
    if isinstance(context_data.get("columns"), dict):
        context_data["columns"] = [{"name": key, **value} for key, value in context_data["columns"].items()]

    # Ensure context_data["columns"] is a list of dictionaries
    if not isinstance(context_data["columns"], list) or not all(isinstance(col, dict) for col in context_data["columns"]):
        raise TypeError(f"ERROR: Expected a list of dictionaries in '{context_name}', but got {type(context_data.get('columns'))}: {context_data.get('columns')}")

    return context_data["columns"]
