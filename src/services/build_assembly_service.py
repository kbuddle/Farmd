from models.assembly import Assembly
from services.assembly_parts_fetcher import AssemblyPartsFetcher
from ui.component_picker_window import ComponentPickerWindow


class BuildAssemblyService:
    def __init__(self, db_service, parent_window, assembly_id):
        self.db_service = db_service  # ✅ Store database service for queries
        self.assembly = Assembly.fetch_from_db(assembly_id)
        self.parts_fetcher = AssemblyPartsFetcher()
        self.parent_window = parent_window
        self.all_parts = self.parts_fetcher.fetch_available_items(self.assembly.item_id)  # ✅ Store full dataset
        self.filter_enabled = False  # ✅ Toggle state for filtering
        self.assembly_id = assembly_id

        
    
    def toggle_filter(self):
        """Toggles filtering on/off and returns the appropriate color and label."""
        self.filter_enabled = not self.filter_enabled
        color = "green" if self.filter_enabled else "red"
        label = "Filtering: ON" if self.filter_enabled else "Filtering: OFF"
        return color, label
    
    def fetch_available_parts(self, filter_text=""):
        """Returns available parts and assemblies, optionally filtered by name if filtering is enabled."""
        
        # ✅ Fetch parts and assemblies with dynamically assigned EntityType
        query = """
            SELECT PartID AS ID, PartName AS Name, 'Part' AS EntityType FROM Parts
            UNION ALL
            SELECT AssemblyID AS ID, AssemName AS Name, 'Assembly' AS EntityType FROM Assemblies
        """
        self.all_parts = self.db_service.fetch_all_dict(query)  # ✅ Store result as dictionary list
        
        # ✅ Apply filtering if enabled
        filter_text = filter_text.lower().strip()
        if self.filter_enabled and filter_text:
            return [part for part in self.all_parts if filter_text in part["Name"].lower()]
        
        return self.all_parts  # ✅ Return full list if no f`iltering is applied

    
    def fetch_assigned_parts(self):
        """Returns currently assigned parts and assemblies."""
        return self.assembly.fetch_available_components()
    
    def add_part(self, part_id, entity_type, quantity=1, unit="each"):
        from ui.build_assembly_window import BuildAssemblyWindow
        
        """Assigns a part to the assembly and updates available parts."""
        self.assembly.add_part(part_id, entity_type, quantity, unit)
        self.all_parts = self.parts_fetcher.fetch_available_items(self.assembly.item_id)  # Refresh list after addition
        
         # Instantiate build window only when needed
        if not hasattr(self, "build_window"):
            self.build_window = BuildAssemblyWindow(self.parent_window, self.assembly.item_id, self.assembly.name)
            
        self.build_window.populate_assigned_parts()
        self.update_build_button_state()
    
    def remove_part(self, part_id):
        """Marks a part as deleted (soft delete) rather than removing it permanently."""
        from ui.build_assembly_window import BuildAssemblyWindow
        
        # Instantiate build window only when needed
        if not hasattr(self, "build_window"):
            self.build_window = BuildAssemblyWindow(self.parent_window, self.assembly.item_id, self.assembly.name)

        self.assembly.mark_part_deleted(part_id)
        self.all_parts = self.parts_fetcher.fetch_available_items(self.assembly.item_id)  # Refresh list after removal
        self.build_window.populate_assigned_parts()
        self.update_build_button_state()
    
    def open_component_picker(self):
        """Opens the component picker window to add new components."""
        ComponentPickerWindow(self.parent_window, self.assembly.item_id, self.add_part)
    
    def update_build_button_state(self):
        """Disables the Build button if no valid assembly is selected."""
        if hasattr(self.parent_window, 'build_button'):
            assigned_parts = self.fetch_assigned_parts()
            self.parent_window.build_button.config(state="normal" if assigned_parts else "disabled")

    def update_button_states(self, is_new=False):
        """Updates button states based on the selected item or new entry."""
        selected_item = self.parent_window.entity_tree.selection()
        has_selection = bool(selected_item)

        # Enable Save button if adding a new item
        self.parent_window.buttons["Save Changes"].config(state="normal" if is_new or has_selection else "disabled")

        # Enable Clone, Delete only if an item is selected
        self.parent_window.buttons["Clone Item"].config(state="normal" if has_selection else "disabled")
        self.parent_window.buttons["Delete Item"].config(state="normal" if has_selection else "disabled")

        # Enable Build button only if an assembly is selected
        if "Build" in self.parent_window.buttons:
            entity_type = self.parent_window.entity_name.lower()
            self.parent_window.buttons["Build"].config(state="normal" if has_selection and entity_type == "assemblies" else "disabled")
