# subject to redistribution within new filing structure.

from ui.ui_components import create_card_frame
from src.database.database_utils import get_entity_details

def on_datasheet_selection(event, table, parent_frame, entity_type):
    """
    Handles row selection in the datasheet and updates the card frame.

    Args:
        event: The event that triggered the selection.
        table (ttk.Treeview): The datasheet table widget.
        parent_frame (tk.Frame): The parent frame where `create_card_frame` will be displayed.
        entity_type (str): The type of entity being selected (e.g., "Assemblies", "Parts", "Suppliers").
    """
    selected_item = table.selection()
    if not selected_item:
        print("DEBUG: No item selected.")
        return

    print(f"DEBUG: The selected item from the table is {selected_item}")

    # ✅ Ensure `entity_id` is extracted correctly
    entity_id = table.item(selected_item, "values")[0]
    try:
        entity_id = int(entity_id)  # Ensure integer type if IDs are numeric
    except ValueError:
        print(f"❌ ERROR: Entity ID '{entity_id}' is not a valid integer.")
        return

    print(f"DEBUG: Selected {entity_type} with ID {entity_id}")

    # ✅ Fetch entity details from the database
    entity_details = get_entity_details(entity_id, entity_type)
    if not entity_details:
        print(f"❌ ERROR: No details found for {entity_type} with ID {entity_id}")
        return

    print(f"DEBUG: Retrieved details: {entity_details}")

    # ✅ Clear the existing frame before updating
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ✅ Create a new card frame with the retrieved entity details
    create_card_frame(parent_frame, entity_details, view_name="card_view")
    print(f"✅ SUCCESS: Updated card view for {entity_type} with ID {entity_id}")

