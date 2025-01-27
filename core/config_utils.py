from config.config_data import COLUMN_DEFINITIONS, DEBUG

def get_column_attribute_for_context(context, attribute):
    """
    Retrieve a list of specified attributes for a given context from COLUMN_DEFINITIONS.
    
    from core.config_utils import get_column_attribute_for_context

    Args:
        context (str): The table or context name (e.g., "Assemblies").
        attribute (str): The attribute to extract (e.g., "display_name", "width").

    Returns:
        list: A list of attribute values for each column in the specified context.
    """
    # Ensure the context exists in COLUMN_DEFINITIONS and has a "columns" key
    columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})

    # Return a list of the specified attribute for each column
    return [
        col_props.get(attribute)
        for col_name, col_props in columns.items()
        if attribute in col_props
    ]

