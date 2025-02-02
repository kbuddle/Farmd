import tkinter as tk
from src.models.item import Assembly, Part, Supplier
from ui.ui_helpers import create_buttons_frame

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

    # ✅ Get correct entity class dynamically
    entity_class = {
        "Assemblies": Assembly,
        "Parts": Part,
        "Suppliers": Supplier
    }.get(context_name, None)

    if not entity_class:
        raise ValueError(f"Invalid context: {context_name}")

    entity = entity_class(db_manager)  # ✅ Instantiate entity

    # ✅ Define CRUD operations using Item methods
    def add_item(context, insert_query, fetch_query):
        entity.add({})  # TODO: Replace with real form data

    def edit_item(context, fetch_query, update_query):
        entity.edit(1, {})  # TODO: Replace with selected item ID & form data

    def clone_item(context):
        entity.clone(1)  # TODO: Replace with selected item ID

    def delete_item(context):
        entity.delete(1)  # TODO: Replace with selected item ID

    # ✅ Add Buttons using our refactored `create_buttons_frame`
    create_buttons_frame(tab_frame, context_name, add_item, edit_item, clone_item, delete_item)

    return tab_frame
