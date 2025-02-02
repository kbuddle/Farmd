import tkinter as tk
from tkinter import Frame, Button
from src.ui.ui_events import on_assembly_selection
from src.ui.ui_components import create_assemblies_table
from src.core.service_container import ServiceContainer

class AssembliesScreen:
    """Handles the UI layout and interaction for the Assemblies module."""

    def __init__(self, parent, on_back_callback):
        """
        Initializes the Assemblies UI.

        Args:
            parent (tk.Widget): The parent container where the UI is placed.
            on_back_callback (function): Function to return to the main menu.
        """
        self.parent = parent
        self.on_back_callback = on_back_callback
        self.services = ServiceContainer()
        self.datasheet_manager = self.services.get_datasheet_manager("Assemblies")

        self.create_ui()

    def create_ui(self):
        """Builds the UI layout for the Assemblies module."""
        self.clear_parent()

        self.assemblies_container = Frame(self.parent)
        self.assemblies_container.pack(fill="both", expand=True)

        self.card_frame = Frame(self.assemblies_container, relief="sunken", borderwidth=2)
        self.card_frame.pack(fill="x", expand=True, padx=5, pady=5)

        self.parts_container = Frame(self.parent, relief="ridge", borderwidth=2)
        self.parts_container.pack(fill="both", expand=True)

        self.assemblies_frame, self.assemblies_table = create_assemblies_table(self.assemblies_container)

        # ✅ Bind selection event
        self.assemblies_table.bind("<<TreeviewSelect>>", self.on_table_selection)

        # ✅ Back Button
        Button(self.assemblies_container, text="Back to Main", command=self.on_back_callback).pack(pady=10)

    def clear_parent(self):
        """Clears all widgets in the parent container before loading a new module."""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def on_table_selection(self, event):
        """Handles selection event for the assemblies table."""
        on_assembly_selection(event, self.assemblies_table, self.card_frame, self.parts_container)
