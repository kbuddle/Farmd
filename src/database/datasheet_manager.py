from src.database.database_service import DatabaseService
class DatasheetManager:
    """Handles data processing for datasheets."""

    def __init__(self, context_name, database_service):
        """
        Args:
            context_name (str): Entity type (e.g., "Assemblies", "Parts").
            db_service (DatabaseService): Database service instance.
        """
        self.context_name = context_name
        self.database_service = database_service  # ✅ Dependency Injected

    def add_item(self, data):
        """Handles adding a new record."""
        return self.database_service.add_item(self.context_name, data)

    def edit_item(self, item_id, updated_data):
        """Handles editing an existing record."""
        return self.database_service.update_item(self.context_name, item_id, updated_data)

    def clone_item(self, item_id):
        """Handles cloning an existing record."""
        return self.database_service.clone_item(self.context_name, item_id)

    def delete_item(self, item_id):
        """Handles deleting an existing record."""
        return self.database_service.delete_item(self.context_name, item_id)

    def fetch_items(self):
        """Fetches all records for this datasheet."""
        return self.database_service.fetch_all(self.context_name)