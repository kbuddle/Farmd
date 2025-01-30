import os
from tkinter import Frame, Label, Button, ttk, messagebox
from PIL import Image, ImageTk
from config.config_data import VIEW_DEFINITIONS, DEBUG
from core.database_utils import get_assembly_image  # Function to retrieve image path
from core.database_utils import get_processed_column_definitions
from ui.shared_utils import populate_table, sort_table


def create_card_frame(parent_frame, entity_data, view_name="card_view", on_edit_callback=None):
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
    from ui.ui_events import on_datasheet_selection
    from core.query_builder import query_generator
    if debug:
        print(f"Creating datasheet for context: {context_name}")

    table_frame = Frame(parent_widget, width=1400)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

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
    treeview.pack(side="left", fill="both", expand=True)

    # Configure columns
    for col, details in processed_columns.items():
        treeview.heading(col, text=details.get("display_name", col), command=lambda c=col: sort_table(treeview, c, fetch_query))
        treeview.column(col, width=details.get("width", 100), anchor="w", stretch=False)

    queries = query_generator(context_name)
    fetch_query = queries.get("fetch_query", None)

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



def create_available_parts_view(parent_frame, assembly_id, on_select_callback=None, debug=DEBUG):
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
    from ui.shared_utils import sort_table
    from core.database_queries import fetch_available_items


    if debug:
        print(f"Creating available parts view for assembly: {assembly_id}")

    # Create frame for the datatable
    table_frame = Frame(parent_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create Treeview
    columns = ["ID", "Name", "EntityType", "Dimensions", "Model", "Make", "Manufacturer", "ManPartNum"]
    treeview = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=treeview.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=treeview.xview)
    treeview.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    treeview.pack(side="left", fill="both", expand=True)

    # Configure column headings and sorting
    for col in columns:
        treeview.heading(col, text=col, command=lambda c=col: sort_table(treeview, c, None))
        treeview.column(col, width=150, anchor="w", stretch=False)

    # ✅ Create a search filter
    search_var = StringVar()
    search_entry = Entry(table_frame, textvariable=search_var)
    search_entry.pack(fill="x", padx=5, pady=5)

    def update_table():
        """Filters the table based on the search query."""
        query = search_var.get().lower()
        treeview.delete(*treeview.get_children())  # Clear existing data
        available_items = fetch_available_items(assembly_id)

        for item in available_items:
            if query in item["Name"].lower():  # ✅ Apply filter based on Name
                treeview.insert("", "end", values=list(item.values()))

    search_entry.bind("<KeyRelease>", lambda event: update_table())

    # ✅ Populate the table initially
    update_table()

    # ✅ Handle row selection
    def on_row_select(event):
        selected_item = treeview.selection()
        if selected_item and on_select_callback:
            item_data = treeview.item(selected_item, "values")
            on_select_callback(item_data)

    treeview.bind("<<TreeviewSelect>>", on_row_select)

    return treeview
