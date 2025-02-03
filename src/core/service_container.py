import logging
from src.database.database_service import DatabaseService
from src.database.database_manager import DatabaseManager
from src.ui.datasheet_ui import DatasheetUI
from src.database.datasheet_manager import DatasheetManager
from config.config_data import DATABASE_PATH
class ServiceContainer:
    """Centralized container to manage service dependencies."""

    def __init__(self):
        
        # Initialize core services
        self.database_manager = DatabaseManager()  
        self.database_service = DatabaseService(DATABASE_PATH)  

    def get_datasheet_manager(self, context_name):
        """Returns an instance of DatasheetManager for a specific context."""
        return DatasheetManager(context_name, self.database_service)

    def get_datasheet_ui(self, parent, context_name):
        """Returns an instance of DatasheetUI."""
        datasheet_manager = self.get_datasheet_manager(context_name)
        return DatasheetUI(parent, context_name, datasheet_manager)
