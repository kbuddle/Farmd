from config.config_data import COLUMN_DEFINITIONS, DEBUG


def query_generator(context):
    """
    Generates SQL queries dynamically based on the context.

    Args:
        context (str): The table or context name (e.g., "Assemblies", "Parts").

    Returns:
        dict: A dictionary containing SQL queries for fetch, insert, update, and delete operations.
    """
    column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not column_definitions:
        raise ValueError(f"No column definitions found for context: {context}")

    # Generate the fetch query
    fetch_query = f"SELECT {', '.join(column_definitions.keys())} FROM {context}"

    # Generate the insert query
    insertable_columns = [
        col for col, details in column_definitions.items()
        if not details.get("admin", False) and col != "id"
    ]
    insert_query = (
        f"INSERT INTO {context} ({', '.join(insertable_columns)}) "
        f"VALUES ({', '.join(f':{col}' for col in insertable_columns)})"
    )

    # Generate the update query
    updateable_columns = [
        col for col in column_definitions.keys()
        if not column_definitions[col].get("admin", False) and col != "id"
    ]
    update_query = (
        f"UPDATE {context} SET {', '.join(f'{col} = :{col}' for col in updateable_columns)} WHERE id = :id"
    )

    # Generate the delete query
    delete_query = f"DELETE FROM {context} WHERE id = :id"

    # Return all queries as a dictionary
    return {
        "fetch_query": fetch_query,
        "insert_query": insert_query,
        "update_query": update_query,
        "delete_query": delete_query,
    }


def generate_insert_query(table_name, column_definitions, primary_key=None):
    """
    Generates a dynamic INSERT query with placeholders based on column definitions.

    Args:
        table_name (str): The name of the database table.
        column_definitions (dict): Dictionary of column definitions.
        primary_key (str, optional): The primary key column.

    Returns:
        str: The dynamically generated INSERT query.
    """
    # Exclude columns that should not be inserted (e.g., auto-increment or read-only)
    insertable_columns = [
        col for col, details in column_definitions.items()
        if col != primary_key and ("default" in details and details["default"] is not None or details["type"] not in ["int", "blob"])
    ]

    # Generate the bindings
    placeholders = ", ".join(f":{col}" for col in insertable_columns)

    # Generate the column names
    columns = ", ".join(insertable_columns)

    # Build the query
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    return query


def generate_fetch_query(mode, table_name, column_definitions, where_conditions=None, order_by=None, exclude_admin_columns=True):
    """
    Generates a dynamic SELECT query based on the provided mode and parameters.

    Args:
        mode (str): Query mode - "Basic", "Where", or "WhereAndSort".
        table_name (str): The name of the database table.
        column_definitions (dict): Dictionary of column definitions.
        where_conditions (dict, optional): Conditions for the WHERE clause (e.g., {"Column": "Value"}).
        order_by (str, optional): Column to sort by (e.g., "ColumnName ASC").
        exclude_admin_columns (bool, optional): Whether to exclude admin columns.

    Returns:
        str: The dynamically generated SELECT query.

    Raises:
        ValueError: If the mode is invalid or required parameters are missing.
    """
    # Filter columns based on exclusion rules
    columns = [
        col for col, details in column_definitions.items()
        if not (exclude_admin_columns and details.get("admin", False))
    ]

    # Base SELECT query
    base_query = f"SELECT {', '.join(columns)} FROM {table_name}"

    # Match the mode to construct the query
    match mode:
        case "Basic":
            return base_query

        case "Where":
            if not where_conditions:
                raise ValueError("WHERE conditions must be provided for mode 'Where'.")
            where_clauses = [f"{col} = :{col}" for col in where_conditions.keys()]
            return f"{base_query} WHERE {' AND '.join(where_clauses)}"

        case "WhereAndSort":
            if not where_conditions or not order_by:
                raise ValueError("WHERE conditions and ORDER BY must be provided for mode 'WhereAndSort'.")
            where_clauses = [f"{col} = :{col}" for col in where_conditions.keys()]
            return f"{base_query} WHERE {' AND '.join(where_clauses)} ORDER BY {order_by}"

        case _:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: 'Basic', 'Where', 'WhereAndSort'.")


def generate_update_query(table_name, column_definitions, primary_key):
    """
    Generates a dynamic UPDATE query with positional placeholders.

    Args:
        table_name (str): The name of the database table.
        column_definitions (dict): Dictionary of column definitions.
        primary_key (str): The primary key column.

    Returns:
        str: The dynamically generated UPDATE query with placeholders.
    """
    # Extract column names to update, excluding the primary key
    updatable_columns = [
        col for col in column_definitions.keys()
        if col != primary_key
    ]

    # Create the SET clause with positional placeholders
    set_clause = ", ".join(f"{col} = ?" for col in updatable_columns)

    # Build the query with WHERE clause using ?
    query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
    return query


def generate_delete_query(table_name, primary_key):
    """
    Generates a DELETE query for a given table and primary key.

    Args:
        table_name (str): The name of the table.
        primary_key (str): The name of the primary key column.

    Returns:
        str: The dynamically generated DELETE query.
    """
    delete_query = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
    return delete_query


def generate_sort_query(base_query, sort_column, sort_direction, column_definitions):
    """
    Generates a dynamic SORT query for a given base query.

    Args:
        base_query (str): The base SELECT query.
        sort_column (str): The column to sort by.
        sort_direction (str): The sort direction (ASC or DESC).
        column_definitions (dict): Dictionary of column definitions.

    Returns:
        str: The dynamically generated SORT query.

    Raises:
        ValueError: If the sort column is invalid.
    """
    if sort_column not in column_definitions:
        raise ValueError(f"Invalid sort column: {sort_column}")

    return f"{base_query} ORDER BY {sort_column} {sort_direction}"
