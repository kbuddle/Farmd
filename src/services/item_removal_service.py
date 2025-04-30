
from database.database_manager import DatabaseManager
from ui.build_assembly_window import BuildAssemblyWindow

class ItemRemovalService:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.build_window = None

    def remove_item(self, entity_type, entity_id, table_name, additional_params=None):
        """
        Generalized removal function for various entities (part, supplier, drawing, etc.)
        - entity_type: Type of the entity (part, supplier, etc.)
        - entity_id: ID of the entity to be removed
        - table_name: The database table related to the entity (e.g., 'Assemblies_Parts', 'Suppliers')
        - additional_params: Any extra parameters (like specific conditions for deletion)
        """
        # Initialize the build window if required
        self.ensure_build_window_initialized()

        # Perform database operation based on entity type
        self.remove_from_database(entity_type, entity_id, table_name, additional_params)

        # Handle UI updates (refreshed for all types)
        self.refresh_ui()

    def remove_from_database(self, entity_type, entity_id, table_name, additional_params):
        """
        General database removal function. It will build and execute the query
        based on entity type and passed parameters.
        """
        query = f"DELETE FROM {table_name} WHERE ID = ?"
        if additional_params:
            query += f" AND {additional_params['condition_column']} = ?"

        # Execute the query to remove the entity
        db_manager = DatabaseManager()
        db_manager.execute_query(query, (entity_id, additional_params.get('condition_value') if additional_params else None), commit=True)

        # Additional handling if needed (e.g., updating procurement type for parts)
        if entity_type == "part":
            self.update_procurement_type()

    def ensure_build_window_initialized(self):
        """ Ensures the build window is initialized if it is not already. """
        if not self.build_window:
            self.build_window = BuildAssemblyWindow(self.parent_window)

    def refresh_ui(self):
        """ Refreshes the UI after any removal. """
        self.build_window.populate_assigned_parts()
        self.update_build_button_state()

    def update_build_button_state(self):
        """ Updates the state of the build button after the removal. """
        print("Updating build button state...")
        # Placeholder for UI button state updates

    def update_procurement_type(self):
        """ Placeholder function to update procurement type when removing a part. """
        print("Updating procurement type...")


