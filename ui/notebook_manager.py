import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports
from config.config_data import DEBUG, DATABASE, COLUMN_DEFINITIONS
from core.database_utils import get_connection, execute_query, close_connection, execute_non_query, process_column_definitions
from ui.ui_helpers import create_buttons_frame
from ui.shared_utils import sort_table, populate_table


def create_datasheet_tab(
    notebook,
    add_item,
    edit_item,
    clone_item,
    delete_item,
    build_assy,
    context=None,
    fetch_query=None,
    insert_query=None,
    update_query=None,
    delete_query=None,
    max_width=1400
):
    """
    Creates a reusable datasheet tab with buttons for operations.

    Args:
        notebook (ttk.Notebook): The parent notebook.
        add_item (function): Function to handle 'Add' operations.
        edit_item (function): Function to handle 'Edit' operations.
        clone_item (function): Function to handle 'Clone' operations.
        delete_item (function): Function to handle 'Delete' operations.
        build_assy (function): Function to handle 'Build Assembly' operations (if applicable).
        context (str, optional): Context of the tab (e.g., "Assemblies").
        fetch_query (str, optional): SQL query to fetch data.
        insert_query (str, optional): SQL query to insert data.
        update_query (str, optional): SQL query to update data.
        delete_query (str, optional): SQL query to delete data.
        max_width (int, optional): Maximum width for the table.

    Returns:
        ttk.Frame: The created tab with its table and buttons.
    """

    if not context:
        raise ValueError("Context must be provided to create a datasheet tab.")

    # Retrieve column definitions as a dictionary
    filtered_columns = process_column_definitions(context)
    print("Filtered Columns:", filtered_columns)  # Debugging output

    # Extract column names and widths from the dictionary
    column_names = list(filtered_columns.keys())
    column_widths = {col: details.get("width", 100) for col, details in filtered_columns.items()}

    # Initialize the tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=context)

    # Create a frame for the table and scrollbars
    table_frame = Frame(tab, width=max_width)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create the Treeview
    treeview = ttk.Treeview(table_frame, columns=column_names, show="headings", selectmode="browse")

    # Add scrollbars to the Treeview
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=treeview.xview)

    treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")

    treeview.pack(side="left", fill="both", expand=True)

    # Configure the Treeview headings and column widths
    for col, details in filtered_columns.items():
        treeview.heading(col, text=details.get("display_name", col), command=lambda c=col: sort_table(treeview, c, fetch_query))
        treeview.column(col, width=details.get("width", 100), anchor="w", stretch=False)

    # Populate the table with data
    try:
        populate_table(treeview, fetch_query)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data for {context}.")
        if DEBUG:
            print(f"Error populating Treeview: {e}")

    # Place the buttons frame below the table
    buttons_frame = Frame(tab)
    buttons_frame.pack(fill="x", padx=10, pady=10)

    # Create the buttons frame for CRUD operations
    create_buttons_frame(
        parent_frame=tab,
        context=context,
        add_item=lambda: add_item(context, treeview, insert_query, fetch_query),
        edit_item=lambda: edit_item(context, treeview, fetch_query, update_query, column_names),
        clone_item=lambda: clone_item(context, treeview, fetch_query, insert_query, column_names),
        delete_item=lambda: delete_item(context, treeview, fetch_query, delete_query),
        table=treeview,
        build_assy=lambda assembly_id: build_assy(table_frame, assembly_id) if context == "Assemblies" else None,
    )

    return tab, treeview
