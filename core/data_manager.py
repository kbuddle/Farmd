def save_data(context, data, is_add, column_definitions):
    """
    Saves data to the database for add or edit operations.

    Args:
        context (str): The context/table name.
        data (dict): The data to save.
        is_add (bool): Whether this is an add or edit operation.
        column_definitions (dict): Column definitions for the table.
    """
    from core.query_builder import query_generator
    from core.database_utils import execute_query  # Hypothetical database execution function

    # Generate queries for the context
    queries = query_generator(context)

    # Fetch primary key
    primary_key = next(
        col for col, details in column_definitions.items() if details.get("is_primary_key", False)
    )

    if is_add:
        # Use the insert query, excluding the primary key
        query = queries["insert_query"]
        params = {k: v for k, v in data.items() if k != primary_key}
    else:
        # Use the update query, including the primary key
        query = queries["update_query"]
        params = data  # Include everything, including the primary key

    # Debugging output
    print(f"Executing query: {query}")
    print(f"With params: {params}")

    # Execute the query
    execute_query(query, params)


from data_manager import save_data

def on_save(context, form_data, is_add):
    """
    Handles the save operation for the data entry form.

    Args:
        context (str): The context/table name.
        form_data (dict): Data collected from the form.
        is_add (bool): Whether this is a new record (add) or an edit.
    """
    save_data(context, form_data, is_add=is_add)