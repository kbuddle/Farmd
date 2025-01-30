import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports
from config.config_data import DEBUG, COLUMN_DEFINITIONS, DATABASE_PATH
from core.database_utils import get_processed_column_definitions, add_item, edit_item, clone_item, delete_item
from ui.ui_helpers import create_buttons_frame
from ui.shared_utils import sort_table, populate_table
from core.query_builder import query_generator
from core.database_transactions import undo_last_action
from ui.ui_helpers import center_window_vertically

from ui.ui_components import create_datasheet_view  # ✅ Import the new function
from ui.ui_events import on_datasheet_selection
from ui.ui_components import create_available_parts_view

def create_datasheet_tab(notebook, context_name, context_data, parent_frame=None, debug=DEBUG):
    """
    Creates a notebook tab for a datasheet and configures buttons, while delegating table creation
    to `create_datasheet_view`.

    Args:
        notebook (ttk.Notebook): The notebook where the tab will be added.
        context_name (str): The name of the context (e.g., "Assemblies", "Parts").
        context_data (dict): Configuration for the datasheet.
        parent_frame (tk.Frame, optional): The frame where entity details will be displayed.
        debug (bool): Enables debug logging.

    Returns:
        tuple: (tab, treeview) - The created notebook tab and the Treeview widget.
    """
    if debug:
        print(f"Creating datasheet tab for context: {context_name}")

    # Generate queries and validate them
    queries = query_generator(context_name)
    print(f"DEBUG: Queries generated for {context_name}: {queries}")  # ✅ Print query output
    
    if not queries or "fetch_query" not in queries or queries["fetch_query"] is None:
        raise ValueError(f"Query generation failed for {context_name}. Received: {queries}")
    

    # Initialize the tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=context_data["name"])
    print(f"Tab '{context_data['name']}' successfully added to the notebook")

    # ✅ Call `create_datasheet_view` to generate the table inside the tab
    table_frame, treeview = create_datasheet_view(tab, context_name, context_data, debug=DEBUG)

    if context_name == "Assemblies":
        create_available_parts_view(tab, assembly_id=1, debug=debug)
               
    # ✅ Bind row selection to update `create_card_frame` (if `parent_frame` exists)
    if parent_frame:
        treeview.bind("<<TreeviewSelect>>", lambda event: on_datasheet_selection(event, treeview, parent_frame, context_name))

    # ✅ Create and place the buttons below the table
    buttons_frame = Frame(tab)
    buttons_frame.pack(fill="x", padx=10, pady=10)

    # CRUD Buttons
    ttk.Button(buttons_frame, text="Add", command=lambda: add_item(context_name, treeview, queries["insert_query"], queries["fetch_query"])).pack(side="left", padx=5, pady=5)
    ttk.Button(buttons_frame, text="Edit", command=lambda: edit_item(context_name, treeview, queries["fetch_query"], queries["update_query"])).pack(side="left", padx=5, pady=5)
    ttk.Button(buttons_frame, text="Clone", command=lambda: clone_item(context_name, treeview, queries["fetch_query"], queries["insert_query"])).pack(side="left", padx=5, pady=5)
    ttk.Button(buttons_frame, text="Delete", command=lambda: delete_item(context_name, treeview, queries["fetch_query"], queries["delete_query"])).pack(side="left", padx=5, pady=5)
    ttk.Button(buttons_frame, text="Undo", command=lambda: undo_last_action(treeview, queries["fetch_query"])).pack(side="left", padx=5, pady=5)

    return tab, treeview
