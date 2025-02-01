# subject to redistribution within new filing structure.

import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar

from config.config_data import DEBUG, COLUMN_DEFINITIONS, VIEW_DEFINITIONS, DATABASE_PATH
from src.core.database_transactions import DatabaseTransactionManager
from src.ui.ui_helpers import center_window_vertically
from src.forms import data_entry_form
# Initialize db_manager once
db_manager = DatabaseTransactionManager(DATABASE_PATH)


def get_connection(db_name=DATABASE_PATH):
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

def add_item(context_name, table=None, insert_query=None, fetch_query=None, post_insert_callback=None, debug=False):
    if debug:
        print(f"Context: {context_name}")
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
    from src.ui.shared_utils import populate_table
    from src.forms.data_entry_form import build_form
    from src.forms.validation import validate_form_data, validate_foreign_keys
   

    # Fetch filtered column definitions
    columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
    if not columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context_name}'.")
        return
    
    # Filter editable columns (exclude admin and primary key columns)
    editable_columns = {
        col_name: col_details
        for col_name, col_details in columns.items()
        if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
    }

    if debug:
        print(f"DEBUG: Editable columns for add_item: {editable_columns}")

    # Build form fields dynamically
    form_window, entry_widgets = build_form(context_name, editable_columns, initial_data={})
  
    def save_item():
        """Handles form submission and saves the item to the database."""
        try:
            # Collect data from the form
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            if debug:
                print(f"DEBUG: Form data for new item: {form_data}")

            # Insert into the database and commit
            db_manager.execute_non_query(insert_query, form_data, commit=False)

            # Ask user if they want to finalize the addition
            confirm = messagebox.askyesno("Confirm Save", "Do you want to save this item permanently?")
            if confirm:
                db_manager.commit_transaction()
                if debug:
                    print("DEBUG: User confirmed save, transaction committed.")
            
            # Refresh the table with updated data
            if debug:
                print(f"DEBUG: Fetching updated data for {context_name}.")
            rows = db_manager.execute_query(fetch_query)

            # Clear and repopulate the table
            table.delete(*table.get_children())
            for row in rows:
                table.insert("", "end", values=tuple(row.values()))

            messagebox.showinfo("Success", f"New {context_name} added successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add new {context_name}: {e}")
            print(f"DEBUG: Error while adding new item: {e}")

   # Add Save button
    save_button = tk.Button(form_window, text="Save", command=save_item, bg="green", fg="white")
    save_button.grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")

    # Add Cancel button
    cancel_button = tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white")
    cancel_button.grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")

    form_window.mainloop()

def update_item_in_db(context, columns, form_data, update_query, debug=False):
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

        # Execute the update query
        db_manager.execute_non_query(update_query, params)
        
        if debug:
            print(f"DEBUG: Update successful for context: {context}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update the {context}: {e}")
        print(f"ERROR: {e}")
        raise

def edit_item(context, table, fetch_query, update_query, debug=False):
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
    from src.core.database_transactions import db_manager
    from src.forms.validation import validate_form_data
    from src.forms.data_entry_form import build_form

    
    # Fetch all column definitions
    all_columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
    if not all_columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context}'.")
        return

    if debug:
        print(f"DEBUG: All columns for edit_item: {all_columns}")

    # Filter editable columns (exclude admin fields)
    editable_columns = {
        col_name: col_details
        for col_name, col_details in all_columns.items()
        if not col_details.get("admin", False)
    }
    if debug:
        print(f"DEBUG: Editable columns: {editable_columns}")

    # Fetch initial data for the form
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected for editing.")
        return

    initial_data = {col_name: table.set(selected_item, col_name) for col_name in editable_columns.keys()}
    if debug:
        print(f"DEBUG: Initial data for edit form: {initial_data}")

    # Build the form
    form_window, entry_widgets = build_form(context, editable_columns, initial_data)

    def save_changes(debug=False):
        try:
            # Collect form data
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            if debug:
                print(f"DEBUG: Form data collected for {context}: {form_data}")

            # Validate form data before updating
            validate_form_data(context, form_data)

            # Update the database
            # Update the database and commit
            db_manager.execute_non_query(update_query, form_data, commit=False)

            # Ask user if they want to finalize the update
            confirm = messagebox.askyesno("Confirm Save", "Do you want to save these changes?")
            if confirm:
                db_manager.commit_transaction()
                print("DEBUG: User confirmed edit, transaction committed.")
                messagebox.showinfo("Success", f"{context} updated successfully.")

            else:
                print("DEBUG: User did not confirm edit, keeping transaction open for rollback.")  

            #Fetch updated data and refresh the table
            if debug:
                print(f"DEBUG: Fetching updated data for {context}.")
            rows = db_manager.execute_query(fetch_query)

            # Clear the table and repopulate with fresh data
            table.delete(*table.get_children())
            for row in rows:
                table.insert("", "end", values=tuple(row.values()))

            messagebox.showinfo("Success", f"{context} updated successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")
            print(f"DEBUG: Error while saving changes: {e}")


    # Add Save button with grid layout
    save_button = tk.Button(form_window, text="Save", command=save_changes, bg="green", fg="white")
    save_button.grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")

    # Add Cancel button with grid layout
    cancel_button = tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white")
    cancel_button.grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")
    
def insert_item_in_db(context, columns, form_data, insert_query, debug=False):
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
    import tkinter as tk
    from tkinter import messagebox
    from config.config_data import COLUMN_DEFINITIONS
    from src.core.database_transactions import db_manager
    from src.forms.data_entry_form import build_form
    from src. forms.validation import validate_form_data
    try:
        # Prepare parameters for the INSERT query (excluding primary key)
        params = {
            col_name: form_data.get(col_name, None)
            for col_name in columns.keys()
            if not columns[col_name].get("is_primary_key", False)
        }

        if debug:
            print(f"DEBUG: Insert parameters for {context}: {params}")

        # Execute the insert query using db_manager
        db_manager.execute_non_query(insert_query, params)

        if debug:
            print(f"DEBUG: Insert successful for context: {context}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to insert the cloned {context}: {e}")
        if debug:
            print(f"DEBUG: Error inserting item: {e}")
        raise

def clone_item(context_name, table, fetch_query, insert_query, debug=False):
    """
    Clones an existing item, allows editing, and refreshes the table upon success.

    Args:
        context (str): Context of the item.
        table (ttk.Treeview): The Treeview to update.
        fetch_query (str): SQL query to fetch updated data.
        insert_query (str): SQL INSERT query for cloning the item.
    """
    from src.forms.data_entry_form import build_form
    from src.forms.validation import validate_form_data
    # Fetch all column definitions
    
    all_columns = COLUMN_DEFINITIONS.get(context_name, {}).get("columns", {})
    if not all_columns:
        messagebox.showerror("Configuration Error", f"No column definitions found for context '{context_name}'.")
        return

    if debug:
            print(f"DEBUG: All columns for clone_item: {all_columns}")

    # Filter editable columns (exclude admin fields and primary key)
    editable_columns = {
        col_name: col_details
        for col_name, col_details in all_columns.items()
        if not col_details.get("admin", False) and not col_details.get("is_primary_key", False)
    }
    if debug:
            print(f"DEBUG: Editable columns for clone_item: {editable_columns}")

    # Fetch data for the selected item
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected for cloning.")
        return

    original_data = {col_name: table.set(selected_item, col_name) for col_name in editable_columns.keys()}
    if debug:
            print(f"DEBUG: Original data for cloning: {original_data}")

    # Prepopulate the form with original data for the clone
    form_window, entry_widgets = build_form(context_name, editable_columns, original_data)

    # Save button logic
    def save_clone():
        try:
            # Collect form data
            form_data = {col_name: var.get() for col_name, var in entry_widgets.items()}
            if debug:
                print(f"DEBUG: Form data for cloned item: {form_data}")

            # Validate form data
            if not validate_form_data(context_name, form_data):
                raise ValueError(f"Validation failed for cloned form data: {form_data}")

            # Insert the cloned record into the database
            insert_item_in_db(context_name, all_columns, form_data, insert_query)

            # Refresh the table with updated data
            if debug:
                print(f"DEBUG: Fetching updated data for {context_name}.")
            rows = db_manager.execute_query(fetch_query)

            # Clear and repopulate the table
            table.delete(*table.get_children())
            for row in rows:
                table.insert("", "end", values=tuple(row.values()))

            messagebox.showinfo("Success", f"{context_name} cloned successfully.")
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clone the {context_name}: {e}")
            if debug:
                print(f"DEBUG: Cloning error: {e}")

    # Add Save button with grid layout
    save_button = tk.Button(form_window, text="Save", command=save_clone, bg="green", fg="white")
    save_button.grid(row=len(editable_columns) + 1, column=0, padx=5, pady=5, sticky="w")

    # Add Cancel button with grid layout
    cancel_button = tk.Button(form_window, text="Cancel", command=form_window.destroy, bg="red", fg="white")
    cancel_button.grid(row=len(editable_columns) + 1, column=1, padx=5, pady=5, sticky="e")

    form_window.mainloop()

def delete_item(context, table, fetch_query, delete_query, debug=False):
    """
    Deletes the selected item from the database and refreshes the table.

    Args:
        context (str): Context of the item.
        table (ttk.Treeview): The Treeview to update.
        fetch_query (str): SQL query to fetch updated data.
        delete_query (str): SQL query to delete the item.
    """
    from src.forms.validation import validate_table_selection
    from src.ui.shared_utils import populate_table
    from src.core.database_transactions import db_manager
    from src.core.config_utils import get_primary_key

    primary_key = get_primary_key(context)
    if not primary_key:
        messagebox.showerror("Configuration Error", f"No primary key defined for context '{context}'.")
        return
    
    # Validate selection
    try:
        selected_values = validate_table_selection(table, context)
        if not selected_values:
            raise ValueError("No item selected for deletion.")
        
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
        if debug:
            print(f"DEBUG: Executing delete query: {delete_query} with item_id: {item_id}")

        # Execute the delete query
        db_manager.execute_non_query(delete_query, {primary_key: item_id})

        # Notify user of success
        messagebox.showinfo("Success", f"{context} deleted successfully!")

        # Refresh the table
        if table and fetch_query:
            populate_table(table, fetch_query)

    except Exception as e:
        if debug:
            print(f"DEBUG: Error during deletion: {e}")
        messagebox.showerror("Database Error", f"Error deleting {context}: {e}")

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

def connection_debugger(func):
    
    import functools
    @functools.wraps(func)
    
    def wrapper(*args, **kwargs):
        print(f"DEBUG: {func.__name__} called with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"DEBUG: {func.__name__} completed.")
        return result
    return wrapper

def get_assembly_image(assembly_id):
    """
    Retrieves the image path for a given assembly using db_manager.

    Args:
        assembly_id (int): The ID of the assembly.

    Returns:
        str: File path of the assigned image, or None if no image is linked.
    """
    if not assembly_id:
        return None  # Ensure a valid ID is provided

    query = """
    SELECT i.ImageFileName
    FROM Assemblies a
    JOIN Images i ON a.AssemImageID = i.ImageID
    WHERE a.AssemblyID = ?
    """
    
    result = db_manager.execute_query(query, (assembly_id,))

    return result["ImageFileName"] if result else None  # Return file path or None

def get_entity_details(entity_id, entity_type):
    """
    Fetches details of an entity (Assembly, Part, or Supplier) from the database.

    Args:
        entity_id (int): The ID of the selected entity.
        entity_type (str): The table name where the entity is stored.

    Returns:
        dict: Dictionary containing entity details.
    """
    query = f"SELECT * FROM {entity_type} WHERE ID = ?"
    result = db_manager.execute_query(query, (entity_id,))

    return result[0] if result else {}