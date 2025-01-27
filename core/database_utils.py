import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar

from config.config_data import DEBUG, DATABASE, COLUMN_DEFINITIONS

def get_connection(db_name=DATABASE):
    """
    Establish a connection to the SQLite database with dictionary-based rows.
    :param db_name: Name of the SQLite database file.
    :return: SQLite connection object with dictionary row support.
    """
    try:
        connection = sqlite3.connect(db_name)
        connection.row_factory = sqlite3.Row  # Enable dictionary-based row retrieval
        connection.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign key constraints
        return connection
    except sqlite3.Error as e:
        if DEBUG:
            print(f"Error connecting to database: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")


def execute_query(connection, query, params=None, debug=DEBUG):
    """
    Execute a query on the SQLite database and return results as dictionaries.
    :param connection: SQLite connection object.
    :param query: SQL query string.
    :param params: Optional parameters for the query.
    :return: Fetched rows as a list of dictionaries or None.
    """
    try:
        cursor = connection.cursor()

        # Preprocess params to handle StringVar objects
        if params:
            if isinstance(params, dict):
                params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
            elif isinstance(params, (list, tuple)):
                params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

        # Debugging print
        if debug:
            print(f"Executing query: {query}")
            if params:
                print(f"With parameters: {params}")

        # Execute query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Fetch rows as dictionaries
        if query.strip().lower().startswith("select"):
            result = [dict(row) for row in cursor.fetchall()]
        else:
            connection.commit()
            result = None

        if DEBUG:
            print("Query executed successfully.")
        
        return result

    except Exception as e:
        if debug:
            print(f"Unexpected error: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")
        return None

    finally:
        cursor.close()


def execute_non_query(connection, query, params=None, debug=DEBUG):
    """
    Execute a non-query SQL statement (e.g., INSERT, UPDATE, DELETE).
    :param connection: SQLite connection object.
    :param query: SQL query string.
    :param params: Optional parameters for the query.
    :param debug: Optional flag to enable debugging output.
    """
    try:
        cursor = connection.cursor()

        # Preprocess params to handle StringVar objects
        if params:
            if isinstance(params, dict):
                params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
            elif isinstance(params, (list, tuple)):
                params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

        # Debugging print
        if debug:
            print(f"Executing non-query: {query}")
            if params:
                print(f"With parameters: {params}")

        # Execute query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Commit changes
        connection.commit()

        if debug:
            print("Non-query executed successfully.")

    except sqlite3.Error as e:
        if debug:
            print(f"Error executing non-query: {e}")
        messagebox.showerror("Database Error", f"SQLite error: {e}")
    except Exception as e:
        if debug:
            print(f"Unexpected execute_non_query error: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")
    finally:
        cursor.close()


def close_connection(connection):
    """
    Close the SQLite database connection.
    :param connection: SQLite connection object.
    """
    try:
        connection.close()
    except sqlite3.Error as e:
        if DEBUG:
            print(f"Error closing connection: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")


def fetch_column_definitions(table_name):
    """
    Fetch column definitions for a specific table from the configuration.
    :param table_name: Name of the table.
    :return: Dictionary of column definitions or None if not found.
    """
    return COLUMN_DEFINITIONS.get(table_name, {}).get("columns", {})


def process_column_definitions(context):
    """
    Process column definitions for a specific context while excluding columns with 'admin: True'.

    Args:
        context (str): Context of the table (e.g., "Assemblies").

    Returns:
        dict: Filtered column definitions, preserving the dictionary structure.
    """
    context_config = COLUMN_DEFINITIONS.get(context, {})
    columns = context_config.get("columns", {})

    # Filter out columns with admin: True
    filtered_columns = {
        col: details for col, details in columns.items() if not details.get("admin", False)
    }

    return filtered_columns
