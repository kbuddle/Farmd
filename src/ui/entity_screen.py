import tkinter as tk
from tkinter import Frame, Button
from src.ui.ui_components import create_entity_table
from src.core.service_container import ServiceContainer

class EntityScreen:
    """Generic UI for displaying entities (Parts, Suppliers, etc.) with CRUD operations."""

    def __init__(self, parent, context_name, on_back_callback):
        """
        Initializes the UI for a given entity.

        Args:
            parent (tk.Widget): The parent container where the UI is placed.
            context_name (str): Entity type (e.g., "Parts", "Suppliers").
            on_back_callback (function): Function to return to the main menu.
        """
        self.parent = parent
        self.context_name = context_name
        self.on_back_callback = on_back_callback
        self.services = ServiceContainer()
        self.datasheet_manager = self.services.get_datasheet_manager(context_name)

        self.create_ui()

    def create_ui(self):
        """Builds the UI layout."""
        self.clear_parent()

        self.container = Frame(self.parent)
        self.container.pack(fill="both", expand=True)

        self.table_frame, self.table = create_entity_table(self.container, self.context_name)

        # ✅ Bind selection event for future use (e.g., Edit/Delete)
        self.table.bind("<<TreeviewSelect>>", self.on_table_selection)

        # ✅ CRUD Buttons
        button_frame = Frame(self.container)
        button_frame.pack(fill="x", padx=10, pady=5)

        Button(button_frame, text=f"Add {self.context_name}", command=self.add_item).pack(side="left", padx=10, pady=10)
        Button(button_frame, text=f"Edit {self.context_name}", command=self.edit_item).pack(side="left", padx=10, pady=10)
        Button(button_frame, text=f"Delete {self.context_name}", command=self.delete_item).pack(side="left", padx=10, pady=10)
        Button(button_frame, text="Back to Main", command=self.on_back_callback).pack(side="left", padx=10, pady=10)

        self.populate_table()

    def clear_parent(self):
        """Clears all widgets in the parent container before loading a new module."""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def populate_table(self):
        """Fetches and populates data in the table."""
        self.table.delete(*self.table.get_children())  # Clear previous entries
        rows = self.datasheet_manager.fetch_items()
        for row in rows:
            self.table.insert("", "end", values=row)

    def add_item(self):
        """Handles adding a new item."""
        self.datasheet_manager.add_item({})  # TODO: Replace with form data
        self.populate_table()

    def edit_item(self):
        """Handles editing an existing item."""
        selected_item = self.table.focus()
        if selected_item:
            item_id = self.table.item(selected_item)['values'][0]
            self.datasheet_manager.edit_item(item_id, {})  # TODO: Replace with form data
            self.populate_table()

    def delete_item(self):
        """Handles deleting an item."""
        selected_item = self.table.focus()
        if selected_item:
            item_id = self.table.item(selected_item)['values'][0]
            self.datasheet_manager.delete_item(item_id)
            self.populate_table()

    def on_table_selection(self, event):
        """Handles selection event for the table."""
        print(f"Selected item: {self.table.item(self.table.focus())['values']}")  # Debugging

