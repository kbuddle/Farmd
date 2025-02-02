import tkinter as tk
from tkinter import ttk, Frame, Button

class DatasheetUI:
    """Handles UI for datasheets."""

    def __init__(self, parent, context_name, datasheet_manager):
        """
        Args:
            parent (tk.Widget): Parent UI container.
            context_name (str): Entity type (e.g., "Assemblies", "Parts").
            datasheet_manager (DatasheetManager): Injected dependency.
        """
        self.parent = parent
        self.context_name = context_name
        self.datasheet_manager = datasheet_manager  # ✅ Dependency Injected
        self.create_ui()


    def create_ui(self):
        """Creates the datasheet UI layout."""
        self.table_frame = Frame(self.parent, width=1000, height=600)
        self.table_frame.pack(fill="both", expand=False, padx=10, pady=10)

        self.create_buttons()
        self.create_datasheet_view()

    def create_buttons(self):
        """Creates CRUD operation buttons."""
        button_frame = Frame(self.table_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        def create_button(text, command):
            return Button(button_frame, text=text, command=command).pack(side="left", padx=10, pady=10)

        create_button(f"Add {self.context_name}", self.add_item)
        create_button(f"Edit {self.context_name}", self.edit_item)
        create_button(f"Clone {self.context_name}", self.clone_item)
        create_button(f"Delete {self.context_name}", self.delete_item)

    def create_datasheet_view(self):
        """Creates the Treeview UI for displaying records."""
        self.treeview = ttk.Treeview(self.table_frame, columns=("ID", "Name"), show="headings", selectmode="browse")
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Name", text="Name")

        self.treeview.pack(fill="both", expand=True)
        self.populate_table()

    def populate_table(self):
        """Fetches data and populates the Treeview."""
        self.treeview.delete(*self.treeview.get_children())  # Clear previous entries
        rows = self.datasheet_manager.fetch_items()
        for row in rows:
            self.treeview.insert("", "end", values=row)

    def add_item(self):
        """Triggers add item function in DatasheetManager."""
        self.datasheet_manager.add_item({})  # Replace with actual form data
        self.populate_table()

    def edit_item(self):
        """Triggers edit item function in DatasheetManager."""
        selected_item = self.treeview.focus()
        if selected_item:
            item_id = self.treeview.item(selected_item)['values'][0]
            self.datasheet_manager.edit_item(item_id, {})
            self.populate_table()

    def clone_item(self):
        """Triggers clone item function in DatasheetManager."""
        selected_item = self.treeview.focus()
        if selected_item:
            item_id = self.treeview.item(selected_item)['values'][0]
            self.datasheet_manager.clone_item(item_id)
            self.populate_table()

    def delete_item(self):
        """Triggers delete item function in DatasheetManager."""
        selected_item = self.treeview.focus()
        if selected_item:
            item_id = self.treeview.item(selected_item)['values'][0]
            self.datasheet_manager.delete_item(item_id)
            self.populate_table()
