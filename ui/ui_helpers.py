import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports

def create_buttons_frame(parent_frame, context, add_item, edit_item, clone_item, delete_item, table, build_assy=None):
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
    frame = Frame(parent_frame)
    frame.pack(fill="x", padx=10, pady=5)

    # Add Button
    add_btn = ttk.Button(frame, text="Add", command=add_item)
    add_btn.pack(side="left", padx=5)

    # Edit Button
    edit_btn = ttk.Button(frame, text="Edit", command=edit_item)
    edit_btn.pack(side="left", padx=5)

    # Clone Button
    clone_btn = ttk.Button(frame, text="Clone", command=clone_item)
    clone_btn.pack(side="left", padx=5)

    # Delete Button
    delete_btn = ttk.Button(frame, text="Delete", command=delete_item)
    delete_btn.pack(side="left", padx=5)

    # Context-specific button (e.g., Build Assembly)
    if build_assy:
        build_btn = ttk.Button(frame, text="Build", command=lambda: build_assy(table.focus()))
        build_btn.pack(side="left", padx=5)

    return frame

# Placeholder function for Add
def placeholder_add(context, treeview, insert_query, fetch_query):
    print(f"Add action triggered for context '{context}'")
    # Example: Simulate adding a new row (for UI testing)
    treeview.insert("", "end", values=("New Item", "Placeholder"))

# Placeholder function for Edit
def placeholder_edit(context, treeview, fetch_query, update_query, columns):
    print(f"Edit action triggered for context '{context}'")
    selected_item = treeview.focus()
    if selected_item:
        print(f"Editing item: {treeview.item(selected_item)['values']}")
    else:
        print("No item selected for editing.")

# Placeholder function for Clone
def placeholder_clone(context, treeview, fetch_query, insert_query, columns):
    print(f"Clone action triggered for context '{context}'")
    selected_item = treeview.focus()
    if selected_item:
        print(f"Cloning item: {treeview.item(selected_item)['values']}")
        treeview.insert("", "end", values=treeview.item(selected_item)['values'])
    else:
        print("No item selected for cloning.")

# Placeholder function for Delete
def placeholder_delete(context, treeview, fetch_query, delete_query):
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