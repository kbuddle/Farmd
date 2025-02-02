# subject to redistribution within new filing structure.

# Helper functions for layout adjustments, resizing.

import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar, Button
from tkinter import ttk, Frame  # Consolidated imports
from core.query_builder import query_generator
from src.database.operations import DatabaseOperations

import tkinter as tk
from tkinter import messagebox

class UIHelpers:
    """ Handles UI notifications separately from database logic. """

    @staticmethod
    def show_error(title, message):
        """ Displays an error message in a popup. """
        messagebox.showerror(title, message)

    @staticmethod
    def show_info(title, message):
        """ Displays an informational message in a popup. """
        messagebox.showinfo(title, message)

    @staticmethod
    def ask_confirmation(title, message):
        """ Asks user for confirmation and returns True/False. """
        return messagebox.askyesno(title, message)


def create_buttons_frame(parent_frame, context, on_add, on_edit, on_clone, on_delete, build_assy=None):
    """
    Creates a reusable frame with CRUD operation buttons.

    Args:
        parent_frame (tk.Frame): Parent frame to place the buttons.
        context (str): The entity type (e.g., "Assemblies", "Parts").
        on_add (function): Function to handle item addition.
        on_edit (function): Function to handle item editing.
        on_clone (function): Function to handle item cloning.
        on_delete (function): Function to handle item deletion.
        build_assy (function, optional): Extra function (e.g., for building assemblies).

    Returns:
        tk.Frame: The frame containing all buttons.
    """

    # ✅ Button container
    button_frame = tk.Frame(parent_frame)
    button_frame.pack(fill="x", padx=10, pady=5)

    def create_button(parent, text, command, bg="lightgray"):
        """Creates and returns a button with uniform styling."""
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg="black", padx=10, pady=5)
        btn.pack(side="left", padx=5, pady=5)
        return btn

    # 🔹 Fetch queries outside of UI logic
    queries = query_generator(context)

    # 🔹 Define button actions dynamically
    btn_add = create_button(button_frame, f"Add {context}", lambda: on_add(context, queries["insert_query"], queries["fetch_query"]), bg="green")
    btn_edit = create_button(button_frame, f"Edit {context}", lambda: on_edit(context, queries["fetch_query"], queries["update_query"]), bg="blue")
    btn_clone = create_button(button_frame, f"Clone {context}", lambda: on_clone(context), bg="orange")
    btn_delete = create_button(button_frame, f"Delete {context}", lambda: on_delete(context), bg="red")

    # 🔹 Optionally add a "Build Assembly" button if applicable
    if build_assy:
        create_button(button_frame, f"Build {context}", build_assy, bg="purple")

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

def get_selected_assembly(table):
    """
    Retrieves the selected AssemblyID from the table.
    
    Args:
        table (ttk.Treeview): The assemblies table widget.

    Returns:
        int or None: Selected AssemblyID or None if nothing is selected.
    """
    selected_item = table.selection()
    if not selected_item:
        print("❌ DEBUG: No assembly selected.")
        return None

    assembly_id = table.item(selected_item, "values")[0]
    return int(assembly_id) if assembly_id.isdigit() else None

