# subject to redistribution within new filing structure.
# subject to redistribution within new filing structure.

from src.database.queries import DatabaseQueryExecutor

class Item:
    """ Base class for all database entities (Assemblies, Parts, Suppliers). """
    
    def __init__(self, db_manager, table_name, primary_key="ID"):
        self.db_manager = db_manager
        self.table_name = table_name
        self.primary_key = primary_key
        self.db_query_executor = DatabaseQueryExecutor(db_manager)  # Pass db_manager to query executor

    def add(self, data):
        """ Adds a new item to the database. """
        if not data:
            raise ValueError("Cannot add empty data.")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{col}" for col in data.keys())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        self.db_query_executor.execute_non_query(query, data, commit=True)

    def edit(self, item_id, data):
        """ Updates an existing item in the database. """
        if not data:
            raise ValueError("No data provided for update.")

        update_statements = ", ".join(f"{col} = :{col}" for col in data.keys())
        query = f"UPDATE {self.table_name} SET {update_statements} WHERE {self.primary_key} = :primary_key"
        data["primary_key"] = item_id

        self.db_query_executor.execute_non_query(query, data, commit=True)

    def clone(self, item_id):
        """ Clones an existing item and creates a new one. """
        fetch_query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        item_data = self.db_query_executor.execute_query(fetch_query, (item_id,))
        
        if not item_data:
            raise ValueError(f"Item with ID {item_id} not found for cloning.")

        new_data = {k: v for k, v in item_data[0].items() if k != self.primary_key}  # Exclude PK

        # Insert new cloned item
        self.add(new_data)

    def delete(self, item_id):
        """ Deletes an item from the database. """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        self.db_query_executor.execute_non_query(query, (item_id,), commit=True)

    def fetch_all(self):
        """ Fetches all records for the entity. """
        query = f"SELECT * FROM {self.table_name}"
        return self.db_query_executor.execute_query(query)

    def fetch_by_id(self, item_id):
        """ Fetches a single item by ID. """
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        result = self.db_query_executor.execute_query(query, (item_id,))
        return result[0] if result else None

# 🔹 Subclasses for specific entities

class Assembly(Item):
    """ Represents an Assembly entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, "Assemblies", primary_key="AssemblyID")

class Part(Item):
    """ Represents a Part entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, "Parts", primary_key="PartID")

class Supplier(Item):
    """ Represents a Supplier entity. """
    def __init__(self, db_manager):
        super().__init__(db_manager, "Suppliers", primary_key="SupplierID")
