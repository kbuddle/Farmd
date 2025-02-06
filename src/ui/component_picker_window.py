import tkinter as tk
from tkinter import ttk, messagebox
from services.assembly_parts_fetcher import AssemblyPartsFetcher
from config.config_data import VIEW_DEFINITIONS

class ComponentPickerWindow(tk.Toplevel):
    """UI window for selecting components (Parts or Assemblies) to add to an assembly."""

    def __init__(self, parent, assembly_id, add_callback, view_name="assemblies_parts_view"):
        super().__init__(parent)
        self.title("Select Component")
        self.geometry("750x500")
        self.assembly_id = assembly_id
        self.add_callback = add_callback
        self.fetcher = AssemblyPartsFetcher()
        self.selected_components = {}  # Stores selected components with quantity and unit
        self.unit_options = ["m", "kg", "each"]
        self.view_definition = VIEW_DEFINITIONS.get("AP2", {})
        
        self.create_widgets()
        self.populate_available_components()
    
    def create_widgets(self):
        """Creates UI elements dynamically based on view definitions."""
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.populate_available_components())

        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)

        columns = self.view_definition.get("columns", ["ID", "Name", "Type", "Quantity", "Unit"])
        self.component_list = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")
        
        for col in columns:
            heading_text = self.view_definition.get("headings", {}).get(col, col)
            self.component_list.heading(col, text=heading_text, command=lambda c=col: self.sort_table(c))
            self.component_list.column(col, width=self.view_definition.get("column_widths", {}).get(col, 100), anchor="center", stretch=True)
        
        self.component_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.component_list.bind("<Double-1>", self.edit_quantity)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.assign_button = ttk.Button(button_frame, text="Assign Part(s)", command=self.assign_component, style="success.TButton")
        self.assign_button.pack(side="left", expand=True, padx=5)

        self.commit_button = ttk.Button(button_frame, text="Commit Quantities", command=self.commit_quantities, style="primary.TButton")
        self.commit_button.pack(side="left", expand=True, padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy, style="danger.TButton")
        self.cancel_button.pack(side="right", expand=True, padx=5)
    
    def populate_available_components(self):
        """Fetches and displays available components with filtering."""
        self.component_list.delete(*self.component_list.get_children())
        search_text = self.search_var.get().lower().strip()
        components = self.fetcher.fetch_available_items(self.assembly_id)
        
        filtered_components = [c for c in components if search_text in c["Name"].lower()] if search_text else components
        
        for comp in filtered_components:
            values = tuple(comp.get(col, "") for col in self.view_definition.get("columns", []))
            self.component_list.insert("", "end", values=values)
    
    def sort_table(self, column):
        """Sorts the Treeview table by the selected column."""
        items = [(self.component_list.set(item, column), item) for item in self.component_list.get_children()]
        items.sort()
        for index, (_, item) in enumerate(items):
            self.component_list.move(item, "", index)
    
    def commit_quantities(self):
        """Commits assigned components with their edited quantities and units."""
        for item in self.component_list.get_children():
            component_id = self.component_list.item(item, "values")[0]
            quantity = float(self.component_list.item(item, "values")[3])
            unit = self.component_list.item(item, "values")[4]
            self.add_callback(component_id, quantity, unit)
        self.destroy()
    
    def refresh_entities_on_change(self, entity_form):
        """Automatically refreshes entity view when switching entities."""
        entity_form.populate_entity_tree()
