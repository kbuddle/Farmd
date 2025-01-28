import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar, Button
from tkinter import ttk, Frame  # Consolidated imports
from core.query_builder import query_generator


def create_buttons_frame(parent_frame, context, add_item, edit_item, clone_item, delete_item, table, build_assy=None):
    from core.database_utils import add_item, edit_item
    """
    Creates a frame with buttons for CRUD operations and other context-specific actions.
    :param parent_frame: The parent frame to place the buttons in.
    :param context: The context of the operations (e.g., "Assemblies").
    :param add_item: Function to add a new item.
    :param edit_item: Function to edit the selected item.
    :param clone_item: Function to clone the selected item.
    :param delete_item: Function to delete the selected item.
    :param table: The Treeview widget.
    :param build_assy: Optional function for context-specific operations (e.g., building assemblies).
    """
    button_frame = Frame(parent_frame)
    button_frame.pack(fill="x", padx=10, pady=5)

    def create_button(parent, text, command):    
        """Creates a button with standardized padding and styles."""
        return Button(parent, text=text, command=command).pack(side="left", padx=10, pady=10)   

    # Fetch queries once for reuse

    queries = query_generator(context)
    print(f"Generated Queries for {context}: {queries}")

    # Add common buttons
    create_button(parent=button_frame, text=f"Add {context}", 
        command=lambda: add_item(
        context,
        table,
        insert_query = queries.get("insert_query"),
        fetch_query = queries.get("fetch_query")))

    create_button(parent=button_frame, text=f"Edit {context}",
        command = lambda: edit_item(
        context,
        table,
        fetch_query = queries.get("fetch_query"),
        update_query = queries.get("update_query")))



    create_button(f"Clone {context}", clone_item(context))
    create_button(f"Delete {context}", delete_item(context))
    

    return button_frame

# Placeholder function for Add
def placeholder_add(context, treeview, insert_query, fetch_query, foreign_key_value=None):
    print(f"Context: {context}, Foreign Key Value: {foreign_key_value}")
    if not foreign_key_value:
        raise ValueError(f"Foreign key value is missing for context: {context}")
    print(f"Add action triggered for context '{context}'")
    # Example: Simulate adding a new row (for UI testing)
    treeview.insert("", "end", values=("New Item", "Placeholder"))

# Placeholder function for Edit
def placeholder_edit(context, treeview, fetch_query, update_query, columns, foreign_key_value=None):
    print(f"Context: {context}, Foreign Key Value: {foreign_key_value}")
    if not foreign_key_value:
        raise ValueError(f"Foreign key value is missing for context: {context}")
    print(f"Edit action triggered for context '{context}'")
    selected_item = treeview.focus()
    if selected_item:
        print(f"Editing item: {treeview.item(selected_item)['values']}")
    else:
        print("No item selected for editing.")

# Placeholder function for Clone
def placeholder_clone(context, treeview, fetch_query, insert_query, columns, foreign_key_value=None):
    print(f"Context: {context}, Foreign Key Value: {foreign_key_value}")
    if not foreign_key_value:
        raise ValueError(f"Foreign key value is missing for context: {context}")
    print(f"Clone action triggered for context '{context}'")
    selected_item = treeview.focus()
    if selected_item:
        print(f"Cloning item: {treeview.item(selected_item)['values']}")
        treeview.insert("", "end", values=treeview.item(selected_item)['values'])
    else:
        print("No item selected for cloning.")

# Placeholder function for Delete
def placeholder_delete(context, treeview, fetch_query, delete_query, foreign_key_value=None):
    print(f"Delete action triggered for context '{context}'")
    selected_item = treeview.focus()
    if selected_item:
        print(f"Deleting item: {treeview.item(selected_item)['values']}")
        treeview.delete(selected_item)
    else:
        print("No item selected for deletion.")

# Placeholder function for Build (specific to Assemblies)
def placeholder_build(assembly_id):
    print(f"Build action triggered for assembly ID '{assembly_id}'")

def center_window_vertically(window, width, height):
    """
    Centers a window vertically on the screen.
    
    Args:
        window (tk.Toplevel or tk.Tk): The window to center.
        width (int): The width of the window.
        height (int): The height of the window.
    """
    # Get the screen height
    screen_height = window.winfo_screenheight()
   
    # Calculate the x and y position
    x_position = (window.winfo_screenwidth() - width) // 2  # Horizontally centered
    y_position = (screen_height - height) // 2  # Vertically centered

    # Set the window size and position
    window.geometry(f"{width}x{height}+{x_position}+{y_position}")

def hide_field_in_ui(field_name, value, form_widgets):
    """
    Hides or disables a field in the UI.

    Args:
        field_name (str): The name of the field to hide.
        value (Any): The value to set for the hidden field.
        form_widgets (dict): A dictionary mapping field names to UI widgets.
    """
    widget = form_widgets.get(field_name)
    if widget:
        widget.insert(0, value)  # Populate the value
        widget.config(state="readonly")  # Make it readonly
        widget.grid_remove()  # Optionally hide it entirely

