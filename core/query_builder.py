from config.config_data import COLUMN_DEFINITIONS, DEBUG


def query_generator(context_name):
    """
    Generates SQL queries dynamically based on the context name and column definitions.

    Args:
        context_name (str): The table or context name (e.g., "Suppliers", "Assemblies").

    Returns:
        dict: A dictionary containing SQL queries for fetch, insert, update, and delete operations.
    """
    from core.database_utils import get_processed_column_definitions
    from config.config_data import COLUMN_DEFINITIONS

    print(f"Query generator called for context: {context_name}")

    # Retrieve column definitions from configuration
    context_data = COLUMN_DEFINITIONS.get(context_name)
    if not context_data:
        raise ValueError(f"No column definitions found for context: {context_name}")
  
    columns = context_data["columns"]

    # Process the column definitions
    all_columns = get_processed_column_definitions(columns, exclude_hidden=True)
    print(f"Processed column definitions for contextXXXX '{context_name}': {all_columns}")

    if not isinstance(all_columns, dict):
        raise TypeError(f"'columns' for context '{context_name}' must be a dictionary, got {type(all_columns)}")

    primary_key = next(
        (col for col, details in all_columns.items() if details.get("is_primary_key", False)),
        None
    )
    if not primary_key:
        raise ValueError(f"No primary key defined for context: {context_name}")
    print(f"Primary key for context '{context_name}': {primary_key}")

    # Generate SQL queries
    def generate_fetch_query():
        # Exclude admin columns
        visible_columns = [col for col, details in columns.items() if not details.get("admin", False)]
        
        query = f"SELECT {', '.join(visible_columns)} FROM {context_name}"
        print(f"DEBUG: Generated fetch query for {context_name}: {query}")
        return query

        
        """ query = f"SELECT {', '.join(all_columns.keys())} FROM {context_name}"
        print(f"Generated fetch query for context '{context_name}': {query}")
        return query """

    def generate_insert_query():
        insertable_columns = [
            col for col, details in all_columns.items()
            if not details.get("admin", False) and col != primary_key
        ]
        query = (
            f"INSERT INTO {context_name} ({', '.join(insertable_columns)}) "
            f"VALUES ({', '.join(f':{col}' for col in insertable_columns)})"
        )
        print(f"Generated insert query for context '{context_name}': {query}")
        return query

    def generate_update_query(context_name, columns):
        primary_key = next(
            (col for col, details in columns.items() if details.get("is_primary_key", False)),
            None
        )
        updatable_columns = [
            col for col, details in columns.items()
            if col != primary_key and not details.get("foreign_key", False)
        ]
        set_clause = ", ".join([f"{col} = :{col}" for col in updatable_columns])
        query = f"UPDATE {context_name} SET {set_clause} WHERE {primary_key} = :{primary_key}"
        print(f"Generated update query for context '{context_name}': {query}")
        return query

    def generate_delete_query():
        query = f"DELETE FROM {context_name} WHERE {primary_key} = :{primary_key}"
        print(f"Generated delete query for context '{context_name}': {query}")
        return query

    return {
        "fetch_query": generate_fetch_query(),
        "insert_query": generate_insert_query(),
        "update_query": generate_update_query(context_name, all_columns),
        "delete_query": generate_delete_query(),
    }





def generate_fetch_query_parts(mode, table_name, column_definitions, where_conditions=None, order_by=None, exclude_admin_columns=True):
    """
    Generates a dynamic SELECT query based on the provided mode and parameters.

    Args:
        mode (str): Query mode - "Basic", "Where", or "WhereAndSort".
        table_name (str): The name of the database table.
        column_definitions (dict): Dictionary of column definitions.
        where_conditions (dict, optional): Conditions for the WHERE clause.
        order_by (str, optional): Column to sort by.
        exclude_admin_columns (bool, optional): Whether to exclude admin columns.

    Returns:
        str: The dynamically generated SELECT query.
    """
    # Filter columns based on exclusion rules
    columns = [
        col for col, details in column_definitions.items()
        if not (exclude_admin_columns and details.get("admin", False))
    ]

    # Base SELECT query
    base_query = f"SELECT {', '.join(columns)} FROM {table_name}"

    # Construct the query based on the mode
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





def generate_delete_query_parts(table_name, primary_key):
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
