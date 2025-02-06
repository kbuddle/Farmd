import tkinter as tk
from tkinter import ttk, messagebox
from services.build_assembly_service import BuildAssemblyService
from ui.edit_component import EditComponentWindow


class BuildAssemblyWindow(tk.Toplevel):
    def __init__(self, parent, assembly_id, assembly_name, db_service):
        super().__init__(parent)
        self.title(f"Build Assembly: {assembly_name}")
        self.geometry("700x500")
        self.service = BuildAssemblyService(db_service, parent, assembly_id)
        self.assembly_id = assembly_id
        self.assembly_name = assembly_name
        
        self.create_widgets()
        self.populate_available_parts()
        self.populate_assigned_parts()
    
    def create_widgets(self):
        """Create UI elements for managing assembly parts."""
        self.available_parts_label = ttk.Label(self, text="Available Parts & Assemblies")
        self.available_parts_label.pack()
        
        self.available_parts_list = ttk.Treeview(self, columns=("ID", "Name", "Type"), show="headings")
        self.available_parts_list.heading("ID", text="ID")
        self.available_parts_list.heading("Name", text="Name")
        self.available_parts_list.heading("Type", text="Type")
        self.available_parts_list.pack()
        
        self.add_button = ttk.Button(self, text="Add Selected", command=self.add_part)
        self.add_button.pack()
        
        self.assigned_parts_label = ttk.Label(self, text="Assigned Parts & Assemblies")
        self.assigned_parts_label.pack()
        
        self.assigned_parts_list = ttk.Treeview(self, columns=("ID", "Name", "Quantity"), show="headings")
        self.assigned_parts_list.heading("ID", text="ID")
        self.assigned_parts_list.heading("Name", text="Name")
        self.assigned_parts_list.heading("Quantity", text="Quantity")
        self.assigned_parts_list.pack()
        
        self.edit_button = ttk.Button(self, text="Edit Component", command=self.open_edit_component)
        self.edit_button.pack(pady=5)
        
        self.remove_button = ttk.Button(self, text="Remove Selected", command=self.remove_part)
        self.remove_button.pack()
    
    def populate_available_parts(self):
        """Fetch available parts and add them to the UI (now with correct EntityType)."""
        self.available_parts_list.delete(*self.available_parts_list.get_children())
        
        results = self.service.fetch_available_parts()  # ✅ Now returns EntityType
        print(f"🔍 Available Parts Data: {results}")  # ✅ Debugging output to verify correct format
        
        for part in results:
            print(f"🔍 Part Keys: {part.keys()}")  # ✅ Debugging output
            self.available_parts_list.insert("", "end", values=(part["ID"], part["Name"], part["EntityType"]))  # ✅ Uses new EntityType
    
    def populate_assigned_parts(self):
        """Fetch assigned parts and display them (using dictionaries)."""
        self.assigned_parts_list.delete(*self.assigned_parts_list.get_children())
        
        assigned_parts = self.service.fetch_assigned_parts()  # ✅ Ensure this returns dictionaries
        
        for part in assigned_parts:
            self.assigned_parts_list.insert("", "end", values=(part["PartID"], part["PartName"], part["Quantity"]))

    def add_part(self):
        """Add selected part or assembly to the assembly."""
        selected_item = self.available_parts_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No part selected to add.")
            return

        # ✅ Extract part details using dictionary-based lookup
        part_values = self.available_parts_list.item(selected_item, "values")
        part_id = int(part_values[0])  # First value is PartID
        entity_type = part_values[2]   # Third value should be 'Part' or 'Assembly'

        # ✅ Ensure entity_type is valid
        if entity_type not in ["Part", "Assembly"]:
            messagebox.showerror("Error", f"Invalid EntityType: {entity_type}.")
            return

        # ✅ Pass entity_type when calling add_part()
        self.service.add_part(part_id, entity_type)

        # ✅ Refresh UI
        self.populate_available_parts()
        self.populate_assigned_parts()
  
    def remove_part(self):
        """Remove selected part from the assembly."""
        selected_item = self.assigned_parts_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No part selected to remove.")
            return

        part_values = self.assigned_parts_list.item(selected_item, "values")
        part_id = int(part_values[0])  # ✅ Ensure proper dictionary-based handling
        
        self.service.remove_part(part_id)
        self.populate_available_parts()
        self.populate_assigned_parts()
    
    def open_edit_component(self):
        """Opens the EditComponentWindow for the selected row."""
        selected_item = self.assigned_parts_list.selection()
        if not selected_item:
            return
        
        item_values = self.assigned_parts_list.item(selected_item[0], "values")
        component_id, component_name, current_quantity = item_values[0], item_values[1], float(item_values[2])
        
        EditComponentWindow(self, self.service.assembly_id, component_id, component_name, current_quantity)