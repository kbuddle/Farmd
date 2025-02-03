# subject to redistribution within new filing structure.
# subject to redistribution within new filing structure.

from src.database.database_service import DatabaseService


class Item:
    """ Base class for all database entities (Assemblies, Parts, Suppliers). """
    
    def __init__(self, db_service, table_name, primary_key):
        self.db_service = db_service
        self.table_name = table_name
        self.primary_key = primary_key

    def fetch_all(self):
        return self.db_service.fetch_all(self.table_name)

    def add(self, data):
        self.db_service.add_item(self.table_name, data)

    def update(self, data, item_id):
        self.db_service.update_item(self.table_name, data, item_id)

    def delete(self, item_id):
        self.db_service.delete_item(self.table_name, item_id)

        
# 🔹 Subclasses for specific entities

class Assembly(Item):
    """ Represents an Assembly entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, table_name="Assemblies", primary_key="AssemblyID")

class Part(Item):
    """ Represents a Part entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, table_name="Parts", primary_key="PartID")

class Supplier(Item):
    """ Represents a Supplier entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, table_name="Suppliers", primary_key="SupplierID")
