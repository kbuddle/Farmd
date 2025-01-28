import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports
from config.config_data import DEBUG, DATABASE, COLUMN_DEFINITIONS
from core.database_utils import get_connection, execute_query, close_connection, execute_non_query, get_processed_column_definitions, add_item, edit_item, clone_item, delete_item
from ui.ui_helpers import create_buttons_frame
from ui.shared_utils import sort_table, populate_table
from core.query_builder import query_generator

def create_datasheet_tab(notebook, context_name, context_data):
    print(f"create_datasheet_tab called with context_name: {context_name}")
    print(f"context_data: {context_data}")

    # Validate inputs
    if not isinstance(context_name, str):
        raise ValueError(f"context_name must be a string, got {type(context_name).__name__}")
    if not isinstance(context_data, dict):
        raise ValueError(f"context_data must be a dictionary, got {type(context_data).__name__}")
    if "columns" not in context_data:
        raise KeyError(f"Missing 'columns' key in context_data: {context_data}")

    # Extract and validate columns
    columns = context_data["columns"]
    if not isinstance(columns, dict):
        raise ValueError(f"'columns' must be a dictionary, got {type(columns).__name__}. Value: {columns}")
    print(f"Columns for context '{context_name}': {columns}")

    # Generate queries
    queries = query_generator(context_name)
    print(f"Generated queries for context '{context_name}': {queries}")

    # Process column definitions if needed (optional step)
    processed_columns = get_processed_column_definitions(columns, exclude_hidden=True)
    print(f"Processed columns for context '{context_name}': {processed_columns}")

    # Extract column names and details for Treeview
    column_names = list(processed_columns.keys())
    column_widths = {col: details.get("width", 100) for col, details in processed_columns.items()}

    # Initialize the tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=context_data["name"])
    print(f"Tab '{context_data['name']}' successfully added to the notebook")

    # Create a frame for the table and scrollbars
    table_frame = Frame(tab, width=1400)
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
    for col, details in processed_columns.items():
        print(f"Configuring Treeview column: {col}, Details: {details}")
        treeview.heading(col, text=details.get("display_name", col), command=lambda c=col: sort_table(treeview, c, queries["fetch_query"]))
        treeview.column(col, width=details.get("width", 100), anchor="w", stretch=False)

    # Populate the table with data
    try:
        populate_table(treeview, queries["fetch_query"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data for {context_name}.")
        if DEBUG:
            print(f"Error populating Treeview: {e}")

    # Place the buttons frame below the table
    buttons_frame = Frame(tab)
    buttons_frame.pack(fill="x", padx=10, pady=10)

    # Add buttons for CRUD operations
    ttk.Button(
        buttons_frame,
        text="Add",
        command=lambda: add_item(context_name, treeview, queries["insert_query"], queries["fetch_query"])
    ).pack(side="left", padx=5, pady=5)

    ttk.Button(
        buttons_frame,
        text="Edit",
        command=lambda: edit_item(context_name, treeview, queries["fetch_query"], queries["update_query"])
    ).pack(side="left", padx=5, pady=5)

    ttk.Button(
        buttons_frame,
        text="Clone",
        command=lambda: clone_item(context_name, treeview, queries["fetch_query"], queries["insert_query"])
    ).pack(side="left", padx=5, pady=5)

    ttk.Button(
        buttons_frame,
        text="Delete",
        command=lambda: delete_item(context_name, treeview, queries["fetch_query"], queries["delete_query"])
    ).pack(side="left", padx=5, pady=5)

    return tab, treeview
