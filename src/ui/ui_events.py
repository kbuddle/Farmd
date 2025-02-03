# subject to redistribution within new filing structure.

from tkinter import Toplevel, Frame, Button
from src.ui.ui_components import create_card_frame, create_assigned_parts_table, create_available_parts_table

from src.models.assembly import Assembly
from src.models.part import Part
from src.database.database_manager import DatabaseManager
from src.models.assembly import Assembly  # ✅ Import Assembly class

def on_assembly_selection(event, table, card_frame, parts_container):
    """
    Handles row selection in the Assemblies table and updates both the card frame and assigned parts list.

    Args:
        event: The event that triggered the selection.
        table (ttk.Treeview): The assemblies table widget.
        card_frame (tk.Frame): The frame where the detailed assembly view appears.
        parts_container (tk.Frame): The frame where the assigned parts table appears.
    """
    print("🔍 DEBUG: Assembly selection event triggered")

    selected_item = table.selection()
    if not selected_item:
        print("❌ DEBUG: No assembly selected.")
        return

    # ✅ Get AssemblyID from selection
    assembly_id = int(table.item(selected_item, "values")[0])
    print(f"✅ DEBUG: Selected AssemblyID = {assembly_id}")

    # ✅ Fetch Assembly object
    selected_assembly = Assembly.fetch_from_db(assembly_id)
    if not selected_assembly:
        print(f"❌ ERROR: Assembly {assembly_id} not found in database.")
        return

    print(f"✅ DEBUG: Retrieved Assembly Details: {selected_assembly}")

    # ✅ Clear and update the card frame (upper section)
    for widget in card_frame.winfo_children():
        widget.destroy()
    create_card_frame(card_frame, selected_assembly, view_name="card_view")

    # ✅ Clear and update the assigned parts table (lower section)
    for widget in parts_container.winfo_children():
        widget.destroy()
    assigned_parts_table = create_assigned_parts_table(parts_container, selected_assembly)

    # ✅ Force UI refresh
    card_frame.update_idletasks()
    parts_container.update_idletasks()
    print(f"✅ SUCCESS: UI updated with detailed view and assigned parts for Assembly {assembly_id}")

def on_add_parts(event, available_parts_table, selected_assembly):
    """
    Handles adding selected parts to the assembly.

    Args:
        event: The button click event.
        available_parts_table (ttk.Treeview): The Treeview listing available parts.
        selected_assembly (Assembly): The currently selected Assembly object.
    """
    selected_items = available_parts_table.selection()
    if not selected_items:
        print("DEBUG: No parts selected.")
        return

    selected_parts = []
    for item in selected_items:
        part_values = available_parts_table.item(item, "values")
        part_id = int(part_values[0])  # Assuming first column is PartID
        selected_parts.append(part_id)

    print(f"DEBUG: Selected Parts = {selected_parts}")

    # ✅ Call `add_part()` for each selected part
    for part_id in selected_parts:
        part = Part.fetch_from_db(part_id)  # ✅ Fetch the part from the database
        if part:
            selected_assembly.add_part(part, 1)  # ✅ Default quantity = 1
        else:
            print(f"WARNING: PartID {part_id} not found in database.")

    # ✅ Refresh assigned parts table
    refresh_assigned_parts_table(selected_assembly)

def refresh_assigned_parts_table(assigned_parts_table, assembly_id):
    from ui.shared_utils import populate_table
    
    """
    Refreshes the assigned parts table to reflect updates.
    """
    fetch_query = """
        SELECT p.PartID AS PartID, p.PartName AS PartName, ap.Quantity AS Quantity
        FROM Assemblies_Parts ap
        JOIN Parts p ON ap.PartID = p.PartID
        WHERE ap.ParentAssemblyID = ?
    """
    populate_table(assigned_parts_table, fetch_query, params=(assembly_id,), debug=True)

def populate_table(treeview, fetch_query, params=None, debug=True): 
    """
    Populates the Treeview with data from the database.
    """
    from src.core.database_transactions import db_manager
    
    if debug:
        print(f"🔍 DEBUG: Fetch Query = {fetch_query}, Params = {params}")

    try:
        # ✅ Fetch results from database
        rows = db_manager.execute_query(fetch_query, params=params, debug=debug)

        # ✅ Print fetched rows for debugging
        print(f"✅ DEBUG: Query returned {len(rows)} rows")

        # ✅ Clear existing rows in the Treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        # ✅ Insert rows into the Treeview
        for row in rows:
            treeview.insert("", "end", values=list(row.values()))

    except Exception as e:
        print(f"❌ ERROR in populate_table: {e}")

