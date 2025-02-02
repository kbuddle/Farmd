import tkinter as tk
from tkinter import ttk
from src.models.item import Assembly, Part, Supplier  # ✅ Import subclasses
from ui.ui_helpers import create_buttons_frame
from ui.ui_components import create_datasheet_view

def create_datasheet_tab(parent, context_name, db_manager):
    """
    Creates a datasheet tab for a given context (Assemblies, Parts, Suppliers).

    Args:
        parent (tk.Widget): The parent widget (typically a tab container).
        context_name (str): The entity type.
        db_manager (DatabaseTransactionManager): Database manager instance.

    Returns:
        tk.Frame: The created frame for the datasheet tab.
    """

    tab_frame = tk.Frame(parent)
    tab_frame.pack(fill="both", expand=True)

    # ✅ Dynamically determine the correct entity class
    entity_class = {
        "Assemblies": Assembly,
        "Parts": Part,
        "Suppliers": Supplier
    }.get(context_name)

    if not entity_class:
        raise ValueError(f"Invalid context: {context_name}")

    entity = entity_class(db_manager)  # ✅ Instantiate the class

    # ✅ Create the datasheet view
    table_frame, treeview = create_datasheet_view(tab_frame, context_name, entity)

    # ✅ Define CRUD operations using Item methods
    def add_item():
        """ Calls the add method for the entity. """
        entity.add({})  # TODO: Replace with real form data

    def edit_item():
        """ Calls the edit method for the entity. """
        selected_item = treeview.selection()
        if not selected_item:
            print("No item selected for editing.")
            return
        item_id = treeview.set(selected_item, "ID")  # Assumes "ID" is the primary key column
        entity.edit(item_id, {})  # TODO: Replace with real form data

    def clone_item():
        """ Calls the clone method for the entity. """
        selected_item = treeview.selection()
        if not selected_item:
            print("No item selected for cloning.")
            return
        item_id = treeview.set(selected_item, "ID")
        entity.clone(item_id)

    def delete_item():
        """ Calls the delete method for the entity. """
        selected_item = treeview.selection()
        if not selected_item:
            print("No item selected for deletion.")
            return
        item_id = treeview.set(selected_item, "ID")
        entity.delete(item_id)

    # ✅ Create buttons and pass class methods
    create_buttons_frame(tab_frame, context_name, add_item, edit_item, clone_item, delete_item, treeview)

    return tab_frame
