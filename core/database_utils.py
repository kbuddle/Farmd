import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar

from config.config_data import DEBUG, DATABASE, COLUMN_DEFINITIONS
from ui.ui_helpers import center_window_vertically


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
        """ if debug:
            print(f"Executing query: {query}")
            if params:
                print(f"With parameters: {params}") """

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
        dict: build column definitions, preserving the dictionary structure.
    """
    context_config = COLUMN_DEFINITIONS.get(context, {})
    columns = context_config.get("columns", {})

    # Filter out columns with admin: True
    filtered_columns = {
        col: details for col, details in columns.items() if not details.get("admin", False)
    }

    return filtered_columns

def get_processed_column_definitions(column_definitions, exclude_hidden=True):
    """
    Processes column definitions, optionally filtering out hidden or admin-only columns.

    Args:
        column_definitions (dict): Dictionary of column definitions.
        exclude_hidden (bool): Whether to exclude columns flagged as hidden.

    Returns:
        list: A list of column names, optionally excluding hidden or admin-only columns.
    """
    print(f"get_processed_column_definitions called with:")
    print(f"  column_definitions: {column_definitions} (type: {type(column_definitions)})")
    print(f"  exclude_hidden: {exclude_hidden}")
    
    if not isinstance(column_definitions, dict):
        raise TypeError(f"Expected 'column_definitions' to be a dictionary, got {type(column_definitions).__name__}. Value: {column_definitions}")
    
    print(f"Processing column definitions: {column_definitions}")
    processed_columns= {
        col: details
        for col, details in column_definitions.items()
        if details.get("is_primary_key", False) or not (exclude_hidden and details.get("admin", False))
    }
    
    return processed_columns

def add_item(context, table=None, insert_query=None, fetch_query=None, post_insert_callback=None):
    print(f"Context: {context}")
    print(f"Insert Query: {insert_query}")
    print(f"Fetch Query: {fetch_query}")

    """
    Opens a window to add a new item and refreshes the table upon success.

    Args:
        context (str): Context of the item (e.g., "Assemblies", "Parts").
        table (ttk.Treeview, optional): The Treeview to update. If None, skip Treeview updates.
        insert_query (str, optional): SQL query to insert a new item.
        fetch_query (str, optional): SQL query to fetch updated data. If None, skip fetching.
        post_insert_callback (callable, optional): Function to execute after insertion (e.g., return to build_assembly).
    """
    from ui.shared_utils import populate_table
    from forms.data_entry_form import build_form
    from forms.validation import validate_form_data, validate_foreign_keys

    # Create the form window
    add_item_window = tk.Toplevel()
    add_item_window.title(f"Add {context}")
    center_window_vertically(add_item_window, 600, 750)
    form_frame = tk.Frame(add_item_window)
    form_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Fetch filtered column definitions
    filtered_columns = get_processed_column_definitions(COLUMN_DEFINITIONS[context]["columns"], exclude_hidden=True)
    print("Filtered Columns:", filtered_columns)  # Debugging output

    # Build form fields dynamically
    entry_widgets = build_form(form_frame, context, initial_values=None)

    def save_item():
        """Handles form submission and saves the item to the database."""
        try:
            # Validate and gather form data
            new_item_data = validate_form_data(filtered_columns, entry_widgets)
            print("Validated Form Data:", new_item_data)  # Debugging output

            connection = get_connection()

            # Validate foreign keys
            validate_foreign_keys(new_item_data, filtered_columns, connection)

            # Execute the insert query
            print(f"Executing query: {insert_query} with data: {new_item_data}")  # Debugging
            execute_query(connection, insert_query, new_item_data)
            messagebox.showinfo("Success", f"New {context} added successfully!")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            print(f"Error during insert: {e}")  # Debugging output
            messagebox.showerror("Database Error", f"Failed to add {context}: {e}")
        finally:
            close_connection(connection)

            # Post-insert actions
            if post_insert_callback:
                post_insert_callback()
            if table and fetch_query:
                populate_table(table, fetch_query)

            add_item_window.destroy()

    # Add Save and Cancel buttons
    button_frame = tk.Frame(add_item_window)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Save", command=save_item, bg="green", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=add_item_window.destroy, bg="red", fg="white").pack(side="left", padx=5)

    # Configure modal behavior
    add_item_window.transient()
    add_item_window.grab_set()
    add_item_window.focus_set()

def build_edit_form(context, editable_columns, initial_data):
    """
    Builds a form for editing items, dynamically creating fields based on the column definitions.

    Args:
        context (str): The context of the form (e.g., "Assemblies").
        editable_columns (dict): Dictionary of columns to include in the form.
        initial_data (dict): Dictionary of initial values for the form fields.

    Returns:
        dict: A dictionary of Tkinter StringVars bound to the form fields.
    """
    import tkinter as tk
    from tkinter import ttk, messagebox, Button
    from config.config_data import COLUMN_DEFINITIONS
    from core.database_utils import get_connection, close_connection
    
    form_window = tk.Toplevel()
    form_window.title(f"Edit {context}")

    # Create a dictionary to hold form fields
    entry_widgets = {}

    # Dynamically create form fields
    for row, (col_name, col_details) in enumerate(editable_columns.items()):
        tk.Label(form_window, text=col_details.get("display_name", col_name)).grid(row=row, column=0, sticky="w")
        entry_var = tk.StringVar(value=initial_data.get(col_name, ""))
        entry_widgets[col_name] = entry_var
        ttk.Entry(form_window, textvariable=entry_var).grid(row=row, column=1, sticky="ew")

    return form_window, entry_widgets


def update_item_in_db(context, columns, form_data, update_query):
    """
    Updates a specific item in the database using the provided form data.

    Args:
        context (str): Context of the item (e.g., "Assemblies").
        columns (dict): Column definitions, including admin fields.
        form_data (dict): Data submitted by the user.
        update_query (str): SQL UPDATE query (must include or allow for a WHERE clause).

    Raises:
        Exception: If the database update fails.
    """
    connection = None
    try:
        # Extract the primary key and its value
        primary_key = next(
            (col_name for col_name, col_details in columns.items() if col_details.get("is_primary_key", False)),
            None
        )
        if not primary_key:
            raise ValueError(f"No primary key defined for context: {context}")

        if primary_key not in form_data:
            raise ValueError(f"Primary key '{primary_key}' is missing in the form data.")

        # Prepare parameters
        params = {col_name: form_data.get(col_name, None) for col_name in columns.keys()}
        primary_key_value = form_data.get(primary_key)

        # Ensure the query has a valid WHERE clause
        if "WHERE" not in update_query.upper():
            update_query += f" WHERE {primary_key} = :primary_key_value"
        else:
            # Replace existing WHERE clause with the correct primary key
            update_query = update_query.split("WHERE")[0] + f" WHERE {primary_key} = :primary_key_value"

        # Add primary key value to parameters
        params["primary_key_value"] = primary_key_value

        print(f"DEBUG: Executing update query: {update_query}")
        print(f"DEBUG: With parameters: {params}")

        # Execute the update query
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(update_query, params)
        connection.commit()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update the {context}: {e}")
        raise e

    finally:
        close_connection(connection)



def edit_item(context, table, fetch_query, update_query):
    """
    Opens a window to edit an existing item and refreshes the table upon success.

    Args:
        context (str): Context of the item.
        table (ttk.Treeview): The Treeview to update.
        fetch_query (str): SQL query to fetch updated data.
        update_query (str): SQL query to update the item.
    """
    import tkinter as tk
    from tkinter import ttk, messagebox, Button
    from config.config_data import COLUMN_DEFINITIONS
    from core.database_utils import get_connection, close_connection
    
    # Fetch all column definitions
    all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not all_columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context}'.")
        return

    print(f"DEBUG: All columns for edit_item: {all_columns}")

    # Filter editable columns (exclude admin fields)
    editable_columns = {
        col_name: col_details
        for col_name, col_details in all_columns.items()
        if not col_details.get("admin", False)
    }
    print(f"DEBUG: Editable columns: {editable_columns}")

    # Fetch initial data for the form
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected for editing.")
        return

    initial_data = {col_name: table.set(selected_item, col_name) for col_name in editable_columns.keys()}
    print(f"DEBUG: Initial data for edit form: {initial_data}")

    # Build the form
    form_window, entry_widgets = build_edit_form(context, editable_columns, initial_data)

    # Save button logic
    
    def save_changes():
        """
        Saves the edited data and refreshes the UI table.
        """
        try:
            # Collect form data
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            print(f"DEBUG: Form data collected: {form_data}")

            # Update the database
            update_item_in_db(context, all_columns, form_data, update_query)

            # Refresh the table
            print(f"DEBUG: Fetching updated data for {context}.")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(fetch_query)
            rows = cursor.fetchall()

            # Clear the table and repopulate with fresh data
            table.delete(*table.get_children())
            for row in rows:
                # Convert sqlite3.Row to tuple or list for proper Treeview display
                table.insert("", "end", values=tuple(row))

            # Inform the user and close the form
            messagebox.showinfo("Success", f"{context} updated successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

    # Add Save button with grid
    save_button = tk.Button(form_window, text="Save", command=save_changes, bg="green", fg="white")
    save_button.grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")

    # Add Cancel button with grid
    cancel_button = tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white")
    cancel_button.grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
    

 
def insert_item_in_db(context, columns, form_data, insert_query):
    """
    Inserts a cloned item into the database.

    Args:
        context (str): Context of the item.
        columns (dict): Column definitions, including admin fields.
        form_data (dict): Data collected from the clone form.
        insert_query (str): SQL INSERT query for cloning.

    Raises:
        Exception: If the database insertion fails.
    """
    connection = None
    try:
        # Prepare parameters for the INSERT query
        params = {col_name: form_data.get(col_name, None) for col_name in columns.keys() if not columns[col_name].get("is_primary_key", False)}

        print(f"DEBUG: Insert parameters for {context}: {params}")

        # Execute the insert query
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(insert_query, params)
        connection.commit()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to insert the cloned {context}: {e}")
        raise e

    finally:
        close_connection(connection)

def clone_item(context, table, fetch_query, insert_query):
    """
    Clones an existing item, allows editing, and refreshes the table upon success.

    Args:
        context (str): Context of the item.
        table (ttk.Treeview): The Treeview to update.
        fetch_query (str): SQL query to fetch updated data.
        insert_query (str): SQL INSERT query for cloning the item.
    """
    # Fetch all column definitions
    all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not all_columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context}'.")
        return

    print(f"DEBUG: All columns for clone_item: {all_columns}")

    # Filter editable columns (exclude admin fields and primary key)
    editable_columns = {
        col_name: col_details
        for col_name, col_details in all_columns.items()
        if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
    }
    print(f"DEBUG: Editable columns for clone_item: {editable_columns}")

    # Fetch data for the selected item
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected for cloning.")
        return

    original_data = {col_name: table.set(selected_item, col_name) for col_name in editable_columns.keys()}
    print(f"DEBUG: Original data for cloning: {original_data}")

    # Prepopulate the form with original data for the clone
    form_window, entry_widgets = build_edit_form(context, editable_columns, original_data)

    # Save button logic
    def save_clone():
        try:
            # Collect form data
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            print(f"DEBUG: Form data for cloned item: {form_data}")

            # Insert the cloned record into the database
            insert_item_in_db(context, all_columns, form_data, insert_query)

            # Refresh the table
            print(f"DEBUG: Fetching updated data for {context}.")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(fetch_query)
            rows = cursor.fetchall()

            # Clear and repopulate the table
            table.delete(*table.get_children())
            for row in rows:
                table.insert("", "end", values=tuple(row))

            messagebox.showinfo("Success", f"{context} cloned successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clone the {context}: {e}")

    # Add Save button with grid
    save_button = tk.Button(form_window, text="Save", command=save_clone, bg="green", fg="white")
    save_button.grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")

    # Add Cancel button with grid
    cancel_button = tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white")
    cancel_button.grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
    form_window.mainloop()


def delete_item(context, table, fetch_query, delete_query):
    """
    Deletes the selected item from the database and refreshes the table.

    Args:
        context (str): Context of the item.
        table (ttk.Treeview): The Treeview to update.
        fetch_query (str): SQL query to fetch updated data.
        delete_query (str): SQL query to delete the item.
    """
    from forms.validation import validate_table_selection
    from ui.shared_utils import populate_table

    # Validate selection
    try:
        selected_values = validate_table_selection(table, context)
        item_id = selected_values[0]  # Assuming the first value is the primary key
    except ValueError as e:
        messagebox.showerror("Selection Error", str(e))
        return

    # Confirm deletion
    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to delete this {context} item?\n\nThis action cannot be undone."
    )
    if not confirm:
        return

    # Execute the deletion query
    try:
        connection = get_connection()

        print(f"Executing delete query: {delete_query} with item_id: {item_id}")  # Debug log
        execute_non_query(connection, delete_query, (item_id,))
        connection.commit()

        messagebox.showinfo("Success", f"{context} deleted successfully!")

        # Refresh the table
        if table and fetch_query:
            populate_table(table, fetch_query)

    except Exception as e:
        print(f"Error during deletion: {e}")  # Debug log
        messagebox.showerror("Database Error", f"Error deleting {context}: {e}")
    finally:
        close_connection(connection)


def prepare_update_params(columns, form_data):
    """
    Prepares a dictionary of parameters for an SQL UPDATE query.

    Args:
        columns (dict): Dictionary containing column metadata.
        form_data (dict): Dictionary containing user input data.

    Returns:
        dict: Dictionary with column names as keys and input values as values.
    """
    params = {}

    print(f"DEBUG: Received columns in prepare_update_params: {columns}")
    print(f"DEBUG: Received form_data: {form_data}")

    for col_name, col_details in columns.items():
        # Ensure primary keys and editable fields are processed
        if col_name in form_data:
            value = form_data[col_name]

            # Extract value from StringVar if applicable
            if isinstance(value, tk.StringVar):
                value = value.get()

            params[col_name] = value

    print(f"DEBUG: Prepared update parameters: {params}")
    return params



