from ui.ui_components import create_card_frame
from core.database_utils import get_entity_details

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
        return

    # Retrieve entity ID from the selected row (assuming the first column is the entity ID)
    entity_id = table.item(selected_item, "values")[0]

    # Fetch entity details from the database
    entity_details = get_entity_details(entity_id, entity_type)

    # Clear the existing frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Create a new card frame with the retrieved entity details
    create_card_frame(parent_frame, entity_details, view_name="card_view")
