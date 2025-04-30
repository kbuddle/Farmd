from models.assembly import Assembly
from services.assembly_parts_fetcher import AssemblyPartsFetcher
from ui.component_picker_window import ComponentPickerWindow
from config.config_data import get_ap3_field_mapping
from services.validation_service import ValidationService

from config.config_data import VIEW_DEFINITIONS


class BuildAssemblyService:
    def __init__(self, db_service, parent_window, assembly_id):
        self.db_service = db_service
        self.parent_window = parent_window
        self.assembly_id = assembly_id
        self.assembly = Assembly(db_service, assembly_id, "Default Name")
        
        self.parts_fetcher = AssemblyPartsFetcher(self.db_service)  # Added parts fetcher initialization
        self.view_definition = VIEW_DEFINITIONS.get("AP3", {})
        self.column_mapping = get_ap3_field_mapping()
        self.columns = list(self.column_mapping.keys())
        self.filter_enabled = False
        self.all_parts = self.fetch_available_parts()
        self.validate = ValidationService(self.column_mapping,self.db_service)

    def get_valid_columns(self):
        return {"PartID", "PartName", "EntityType", "Dimensions", "Model", "Make", "Manufacturer", "ProcurementType"}    
    
    def toggle_filter(self):
        self.filter_enabled = not self.filter_enabled
        color = "green" if self.filter_enabled else "red"
        label = "Filtering: ON" if self.filter_enabled else "Filtering: OFF"
        return color, label
    
    def fetch_available_parts(self, filter_text=""):
        columns_str = ", ".join(self.column_mapping.values())
        query = f"SELECT {columns_str} FROM Parts LEFT JOIN Assemblies ON 1=0 UNION ALL SELECT {columns_str} FROM Assemblies LEFT JOIN Parts ON 1=0"
        all_parts = self.db_service.fetch_all_dict(query)
        filter_text = filter_text.lower().strip()
        if self.filter_enabled and filter_text:
            return [part for part in all_parts if filter_text in part.get("Name", "").lower()]
        return all_parts
    
    def fetch_assigned_parts(self):
        """Returns currently assigned parts and assemblies with correct column references."""

        query = """
        SELECT
            ap.ID,
            COALESCE(p.PartID, a.AssemblyID) AS ID,
            COALESCE(p.PartName, a.AssemName) AS Name,
            ap.Quantity
        FROM Assemblies_Parts ap
        LEFT JOIN Parts p ON ap.PartID = p.PartID
        LEFT JOIN Assemblies a ON ap.ChildAssemblyID = a.AssemblyID
        WHERE ap.ParentAssemblyID = ?
        """

        return self.db_service.fetch_all_dict(query, (self.assembly_id,))
    
    def assign_component_to_assembly(self, component_id, entity_type, quantity=1, unit="each"):
        """Assigns a component (part or assembly) to an assembly while handling NULL constraints correctly."""

         # ✅ Determine if this is a Part or Assembly
        if entity_type == "Part":
            part_id = component_id
            child_assembly_id = None
        elif entity_type == "Assembly":
            part_id = None
            child_assembly_id = component_id
        else:
            raise ValueError(f"❌ Invalid EntityType: {entity_type}. Must be 'Part' or 'Assembly'.")

         # ✅ Call the validation service
        self.validate.validate_assembly_part_assignment(part_id, child_assembly_id)

        # ✅ Execute database insertion
        query = """
        INSERT INTO Assemblies_Parts (ParentAssemblyID, PartID, ChildAssemblyID, Quantity, Units, EntityType)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (self.assembly_id, part_id, child_assembly_id, quantity, unit, entity_type)

        self.db_service.execute_query(query, params, commit=True)
        print(f"✅ Successfully assigned {entity_type} with ID {component_id} to Assembly {self.assembly_id}.")

    def remove_part(self, part_id):
        from ui.build_assembly_window import BuildAssemblyWindow
        if not hasattr(self, "build_window"):
            self.build_window = BuildAssemblyWindow(self.parent_window, self.assembly.item_id, self.assembly.name)

        self.assembly.mark_part_deleted(part_id)
        self.all_parts = self.parts_fetcher.fetch_available_items(self.assembly.item_id)
        self.build_window.populate_assigned_parts()
        self.update_build_button_state()
    
    def open_component_picker(self):
        ComponentPickerWindow(self, self.assembly_id, self.assign_component_to_assembly, self.db_service)
    
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
