# subject to redistribution within new filing structure.

# Reusable UI components (frames, buttons, modals).

import tkinter as tk
from tkinter import ttk, Frame, Label, Button
from core.query_builder import query_generator
from src.ui.shared_utils import populate_table, sort_table
from src.core.database_transactions import db_manager
from config.config_data import DEBUG
from src.core.view_management import get_processed_columns

from src.database.database_utils import delete_item, clone_item, add_item, edit_item

class ScrollableFrame(ttk.Frame):
    """A scrollable frame to contain widgets that exceed frame dimensions."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack elements
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Place frame inside canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Resize event to adjust scroll region
        self.scrollable_frame.bind("<Configure>", self._update_scroll_region)

    def _update_scroll_region(self, event=None):
        """Update the scroll region when content changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def create_assemblies_table(parent_widget, debug=True):
    """
    Creates a table (Treeview) to display Assemblies.
    
    Args:
        parent_widget (tk.Widget): Parent frame where the table is displayed.
        debug (bool): Enables debug mode.

    Returns:
        tuple: (Frame, Treeview)
    """
    table_frame = Frame(parent_widget, width=1500, height=600)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ✅ Fetch column definitions dynamically
    column_definitions = get_processed_columns("Assemblies")

    column_definitions_dict= {col["name"]: col for col in column_definitions}

    column_widths = {col["name"]: col.get("width", 150) for col in column_definitions}
    if debug:
        print(f"DEBUG: column_definitions in creating assemblies = {column_definitions}")

    # ✅ Extract column names, display names, and widths
    processed_columns = list(column_definitions_dict.keys())
    display_names = {col["name"]: col.get("display_name", col["name"]) for col in column_definitions}
    column_widths = {col["name"]: col.get("width", 150) for col in column_definitions}  # Default to 150px if missing

    # ✅ Create Treeview
    treeview = ttk.Treeview(table_frame, columns=processed_columns, show="headings", selectmode="browse")

    # ✅ Add scrollbars
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=treeview.xview)
    treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    treeview.pack(side="left", fill="both", expand=True)

    # ✅ Configure columns using correct width lookup
    for col in processed_columns:
        treeview.heading(col, text=display_names[col], command=lambda c=col: sort_table(treeview, c, None))
        treeview.column(col, width=min(column_widths[col], 250), anchor="w", stretch=False)  # ✅ Prevent over-expansion

    # ✅ Fetch & populate data
    fetch_query = "SELECT AssemblyID, AssemName, ProcurementType FROM Assemblies"
    populate_table(treeview, fetch_query, debug=DEBUG)

    return table_frame, treeview

def create_available_parts_view(parent_widget, assembly_id, debug=DEBUG):
    """
    Creates a datatable view for selecting available parts.

    Args:
        parent_frame (tk.Widget): The parent container where the table will be placed.
        assembly_id (int): The ID of the assembly for filtering available parts.
        on_select_callback (function, optional): A callback function for when an item is selected.
        debug (bool): Enables debug logging.

    Returns:
        ttk.Treeview: The created datatable view.
    """
    from tkinter import ttk, Frame, Entry, Label, StringVar
    from src.ui.shared_utils import sort_table, populate_table
    from core.database_queries import fetch_available_items
    from src.core.database_transactions import db_manager

    if debug:
        print(f"Creating available parts view for assembly: {assembly_id}")

    # Create frame for the datatable
    table_frame = Frame(parent_widget)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create Treeview
    processed_columns = ["ID", "Name", "EntityType", "Dimensions", "Model", "Make", "Manufacturer", "ManPartNum"]
    treeview = ttk.Treeview(table_frame, columns=processed_columns, show="headings", selectmode="browse")

    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=treeview.xview)
    treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    treeview.pack(side="left", fill="both", expand=True)

    # Configure column headings and sorting
    for col in processed_columns:
        treeview.heading(col, text=col, command=lambda c=col: sort_table(treeview, c, None))
        treeview.column(col, width=150, anchor="w", stretch=False)

    # Fetch & populate data - Now filtered for selected assembly!
    fetch_query = """
        SELECT p.PartID, p.PartName, ap.Quantity
        FROM Assemblies_Parts ap
        JOIN Parts p ON ap.PartID = p.PartID
        WHERE ap.ID = ?
    """

    populate_table(treeview, fetch_query, params=(assembly_id,), debug=DEBUG)

    return table_frame, treeview

def create_card_frame(parent_widget, assembly, view_name="card_view"):
    """
    Creates a detailed card frame displaying Assembly information, including an image.

    Args:
        parent_widget (tk.Widget): The parent frame where the card will be displayed.
        assembly (Assembly): The selected Assembly object.
        view_name (str): The view mode.
    """
    print(f"🔍 DEBUG: Creating detailed card frame for Assembly {assembly.item_id} inside {parent_widget.winfo_name()}")

    # ✅ Create frame inside the provided parent widget
    card_frame = Frame(parent_widget, name="card_detail_frame", relief="raised", borderwidth=2)
    card_frame.pack(fill="x", expand=True, padx=5, pady=5)

    # ✅ Display Assembly Name
    Label(card_frame, text=f"Assembly: {assembly.name}", font=("Arial", 16, "bold")).pack(pady=5)

    # ✅ Display Assembly Details in Tabular Format
    details_text = f"""
    Assembly ID: {assembly.item_id}
    Procurement Type: {assembly.procurement_type}
    Total Parts: {len(assembly.list_parts())}
    """
    Label(card_frame, text=details_text, font=("Arial", 12)).pack(pady=5)

    # ✅ Display Image (Placeholder for now)
    img_label = Label(card_frame, text="[Image Placeholder]", bg="gray", width=50, height=10)
    img_label.pack(pady=5)

    print(f"✅ SUCCESS: Card frame created for Assembly {assembly.item_id}")

def create_assigned_parts_table(parent_widget, selected_assembly):
    """
    Creates and displays a table (Treeview) for parts assigned to the selected assembly.

    Args:
        parent_widget (tk.Widget): Parent frame where the table is displayed.
        selected_assembly (Assembly): The selected Assembly object.
    """
    print(f"🔍 DEBUG: Creating assigned parts table for Assembly {selected_assembly.item_id}")

    # ✅ Ensure the parent frame is cleared first
    for widget in parent_widget.winfo_children():
        widget.destroy()

    table_frame = Frame(parent_widget, width=1000, height=300)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ✅ Fix fetch query to filter by `ParentAssemblyID`
    fetch_query = """
        SELECT p.PartID AS PartID, p.PartName AS PartName, ap.Quantity AS Quantity
        FROM Assemblies_Parts ap
        JOIN Parts p ON ap.PartID = p.PartID
        WHERE ap.ParentAssemblyID = ?
    """
    
    treeview = ttk.Treeview(table_frame, columns=["PartID", "PartName", "Quantity"], show="headings")
    treeview.pack(fill="both", expand=True)

    print(f"🔍 DEBUG: Running query: {fetch_query} with ParentAssemblyID = {selected_assembly.item_id}")

    # ✅ Pass correct assembly_id to `populate_table()`
    populate_table(treeview, fetch_query, params=(selected_assembly.item_id,), debug=True)

    return treeview

def create_available_parts_table(parent_widget, assembly_id, assigned_parts_table):
    """
    Creates a table displaying parts that are **not yet assigned** to the selected Assembly.

    Args:
        parent_widget (tk.Widget): The frame where the table is displayed.
        assembly_id (int): The selected AssemblyID.
        assigned_parts_table (ttk.Treeview): Reference to the assigned parts table for refreshing.
    """

    table_frame = Frame(parent_widget, width=600)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ["PartID", "PartName"]

    treeview = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")

    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=200, anchor="w", stretch=False)

    treeview.pack(fill="both", expand=True)

    # Fetch available parts (not already assigned)
    fetch_query = """
        SELECT PartID, PartName FROM Parts
        WHERE PartID NOT IN (SELECT PartID FROM Assemblies_Parts WHERE ID = ?)
    """
    populate_table(treeview, fetch_query, params=(assembly_id,))

    def add_selected_parts():
        selected_items = treeview.selection()
        if not selected_items:
            return

        from src.core.database_transactions import db_manager

        insert_query = "INSERT INTO Assemblies_Parts (ProcurementType, ID, PartID, Quantity, EntityType) VALUES (?, ?, ?, ?, ?)"
        for item in selected_items:
            part_id = treeview.item(item, "values")[0]
            db_manager.execute_non_query(insert_query, params=("Purchase", assembly_id, part_id, 1, "Part"), commit=True)

        # Refresh the assigned parts table
        populate_table(assigned_parts_table, "SELECT p.PartID, p.PartName, ap.Quantity FROM Assemblies_Parts ap JOIN Parts p ON ap.PartID = p.PartID WHERE ap.ID = ?", params=(assembly_id,))

    # Add button to confirm selection
    Button(parent_widget, text="Confirm Selection", command=add_selected_parts).pack(pady=10)

def create_assemblies_screen(parent_widget):
    """
    Creates the main assemblies list with action buttons.
    
    Args:
        parent_widget (tk.Widget): The main container for the assemblies screen.
    """
    from src.core.actions import add_item, edit_item, clone_item , delete_item
    
    print("✅ DEBUG: Creating main assemblies screen")
    from src.ui.ui_helpers import get_selected_assembly

    # ✅ Create frame for assemblies list
    table_frame, assemblies_table = create_assemblies_table(parent_widget)

    # ✅ Create button frame below the assemblies list
    button_frame = Frame(parent_widget, name="button_frame")
    button_frame.pack(fill="x", pady=10)

    # ✅ Define buttons
    Button(button_frame, text="Add", command=lambda: add_item()).pack(side="left", padx=5)
    Button(button_frame, text="Edit", command=lambda: edit_item(assemblies_table)).pack(side="left", padx=5)
    Button(button_frame, text="Clone", command=lambda: clone_item(assemblies_table)).pack(side="left", padx=5)
    Button(button_frame, text="Delete", command=lambda: delete_item(assemblies_table)).pack(side="left", padx=5)

    # ✅ "Build" button to open the detail screen
    Button(button_frame, text="Build", command=lambda: on_build(get_selected_assembly(assemblies_table))).pack(side="left", padx=5)

    return assemblies_table

def create_datasheet_view(parent_widget, context_name, context_data, parent_frame=None, debug=False):
    """
    Creates a generic datasheet view that can be used in different layouts.
    
    Args:
        parent_widget (tk.Widget): The parent container where the datasheet is placed.
        context_name (str): The entity type (e.g., "Assemblies", "Parts").
        context_data (dict): Configuration for the datasheet.
        parent_frame (tk.Frame, optional): The frame where entity details will be displayed.
        debug (bool): Enables debug logging.
    
    Returns:
        tuple: (frame, treeview) - The created frame and the Treeview widget.
    """
    from tkinter import Frame, Label, Button, ttk, messagebox
    from ui.ui_events import on_datasheet_selection
    from core.query_builder import query_generator
    from src.database.database_utils import get_processed_column_definitions
    
    if debug:
        print(f"Creating datasheet for context: {context_name}")

    table_frame = Frame(parent_widget, width=1000, height =600)
    table_frame.pack(fill="both", expand=False, padx=10, pady=10)

    # Extract columns
    processed_columns = get_processed_column_definitions(context_data["columns"], exclude_hidden=True)
    column_names = list(processed_columns.keys())

    # Create Treeview
    treeview = ttk.Treeview(table_frame, columns=column_names, show="headings", selectmode="browse")

    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=treeview.xview)
    treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    treeview.pack(side="left", fill="both", expand=False)

    # Configure columns
    for col, details in processed_columns.items():
        treeview.heading(col, text=details.get("display_name", col), command=lambda c=col: sort_table(treeview, c, fetch_query))
        treeview.column(col, width=details.get("width", 100), anchor="w", stretch=False)

    queries = query_generator(context_name)
    fetch_query = queries.get("fetch_query", None)

    if debug:
        print(f" here is what populate table is being called with for fetch_query, {fetch_query}")
    # Populate table
    try:
        populate_table(treeview, fetch_query)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data for {context_name}.")
        if DEBUG:
            print(f"Error populating Treeview: {e}")

    # ✅ Bind row selection dynamically if `parent_frame` is available
    if parent_frame:
        treeview.bind("<<TreeviewSelect>>", lambda event: on_datasheet_selection(event, treeview, parent_frame, context_name))
    
    return table_frame, treeview

def create_card_frame(parent_frame, entity_data, view_name="card_view", on_edit_callback=None, debug=DEBUG):
    """
    Creates a card-style frame dynamically based on VIEW_DEFINITIONS.

    Args:
        parent_frame (tk.Widget): The parent container.
        entity_data (dict): Data for the entity (Assembly, Part, etc.).
        view_name (str): Name of the view mode ('card_view', 'datasheet_view', etc.).
        on_edit_callback (function, optional): Callback function for the edit button.

    Returns:
        Frame: The created card frame.
    """
    import os
    from config.config_data import VIEW_DEFINITIONS, DEBUG
    from src.database.database_utils import get_assembly_image
    from PIL import Image, ImageTk

    # Get the fields to display for the selected view
    fields = VIEW_DEFINITIONS.get(view_name, {}).get("fields", [])

    card_frame = Frame(parent_frame, bd=2, relief="groove", padx=10, pady=10)
    card_frame.pack(fill="x", padx=10, pady=5)

    row_idx = 0

    # Display entity details based on configured fields
    for field in fields:
        value = entity_data.get(field, "N/A")

        Label(card_frame, text=f"{field}:", font=("Arial", 10)).grid(row=row_idx, column=0, sticky="w", padx=5)
        Label(card_frame, text=value, font=("Arial", 10, "bold")).grid(row=row_idx, column=1, sticky="w", padx=5)
        
        row_idx += 1

    # Check for image and display if available
    image_path = get_assembly_image(entity_data.get("AssemblyID"))  # Replace with relevant entity ID lookup

    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((150, 150))
            img = ImageTk.PhotoImage(img)

            img_label = Label(card_frame, image=img)
            img_label.image = img  # Keep reference to prevent garbage collection
            img_label.grid(row=0, column=2, rowspan=row_idx, padx=10, sticky="e")
        except Exception as e:
            print(f"Error loading image: {e}")

    # Edit Button (Optional)
    if on_edit_callback:
        edit_button = Button(card_frame, text="Edit", command=on_edit_callback)
        edit_button.grid(row=row_idx, column=0, pady=5, sticky="w")

    return card_frame




