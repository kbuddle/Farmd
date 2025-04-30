import tkinter as tk
from tkinter import ttk, messagebox
from services.build_assembly_service import BuildAssemblyService
from ui.edit_component import EditComponentWindow
from config.config_data import VIEW_DEFINITIONS, get_ap3_field_mapping
from ui.component_picker_window import ComponentPickerWindow


class BuildAssemblyWindow(tk.Toplevel):
    def __init__(self, parent, assembly_id, assembly_name, db_service):
        super().__init__(parent)
        
        # ✅ Ensure required attributes are initialized
        self.parent_window = parent
        self.assembly_id = assembly_id  # Explicitly assign assembly_id
        self.assembly_name = assembly_name
        self.db_service = db_service  # ✅ Store db_service reference
        
        # ✅ Initialize BuildAssemblyService correctly
        self.service = BuildAssemblyService(db_service, self, assembly_id)
        self.columns = self.service.columns  # ✅ Get column mappings from service
        self.view_definition = VIEW_DEFINITIONS.get("AP3", {})

        # ✅ UI Setup
        self.create_widgets()
        self.populate_available_parts()
        self.populate_assigned_parts()
    
    def create_widgets(self):
        """Create UI elements for managing assembly parts."""
        self.available_parts_label = ttk.Label(self, text="Available Parts & Assemblies")
        self.available_parts_label.pack()
        
        self.available_parts_list = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.available_parts_list.heading(col, text=col)
        self.available_parts_list.pack()
        
        self.add_button = ttk.Button(self, text="Assign Selected Component", command = self.assign_selected_component)
        self.add_button.pack(pady=5)

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

        self.cancel_button = tk.Button(self, text="Cancel", command=self.destroy, bg="red", fg="white")
        self.cancel_button.pack(pady=10)
    
    def populate_available_parts(self):
        """Fetch available parts and add them to the UI (now with correct EntityType)."""
        self.available_parts_list.delete(*self.available_parts_list.get_children())
        for part in self.service.fetch_available_parts():
            values = tuple(part.get(col, "") for col in self.columns)
            self.available_parts_list.insert("", "end", values=values)
    
    def populate_assigned_parts(self):
        """Fetch assigned parts and display them."""
        self.assigned_parts_list.delete(*self.assigned_parts_list.get_children())
        for part in self.service.fetch_assigned_parts():
            values = (part.get("ID", ""), part.get("Name", ""), part.get("Quantity", ""))
            self.assigned_parts_list.insert("", "end", values=values)
   
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

    def open_component_picker(self):
        """Opens the ComponentPickerWindow to allow users to select and assign components to the assembly."""
        ComponentPickerWindow(self, self.assembly_id, self.service.assign_component_to_assembly, self.db_service)

    def assign_selected_component(self):
        """Assigns the selected component from the available list to the assigned list."""
        print(f"selecting an item to assign")

        selected_item = self.available_parts_list.selection()

        if not selected_item:
            print("⚠️ No component selected!")
            return

        # ✅ Fetch the item as a dictionary instead of using a tuple
        selected_values = self.available_parts_list.item(selected_item, "values")  
        
        if not selected_values:
            print("⚠️ Could not retrieve component data!")
            return

        # ✅ Extract dictionary keys dynamically (assuming column mapping exists)
        column_mapping = get_ap3_field_mapping()
        field_names = list(column_mapping.keys())  # Ensure dictionary alignment

        # ✅ Convert tuple into dictionary for proper handling
        component_data = {field_names[i]: selected_values[i] for i in range(len(field_names))}

        # ✅ Now use dictionary-based handling
        component_id = component_data.get("ID")
        entity_type = component_data.get("EntityType", "Part")  # Default to "Part" if missing

        if not component_id:
            print("⚠️ Missing Component ID!")
            return

        # ✅ Assign component immediately instead of opening another window
        self.service.assign_component_to_assembly(component_id, entity_type)

        # ✅ Refresh UI after assignment
        self.refresh_assigned_components()

    def refresh_assigned_components(self):
        self.assigned_parts_list.delete(*self.assigned_parts_list.get_children())  # Clear current list
        assigned_parts = self.service.fetch_assigned_parts()  # Fetch updated list

        for part in assigned_parts:
            values = (part["ID"], part["Name"], part["Quantity"])
            self.assigned_parts_list.insert("", "end", values=values)

        print("🔄 Assigned components list updated!")

    