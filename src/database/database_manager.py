import sqlite3
from config.config_data import DATABASE_PATH, DEBUG, COLUMN_DEFINITIONS
from src.database.database_transaction_manager import DatabaseTransactionManager



class DatabaseManager:
    """Manages all database operations (CRUD) in an OOP approach."""

    def __init__(self, db_path=DATABASE_PATH):
        """Initializes the database manager with a connection and executor."""
        
        self.transaction_manager = DatabaseTransactionManager(db_path)
        
    def get_primary_key(context):
        """Retrieves the primary key column for a given table context."""
        from config.config_data import COLUMN_DEFINITIONS
        
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        
        primary_key = next((col for col, details in column_definitions.items() if details.get("is_primary_key", False)), None)

        if not primary_key:
            raise ValueError(f"No primary key defined for context: {context}")

        return primary_key
    
    def get_connection(self):
        """Returns the active database connection."""
        return self.transaction_manager.get_connection()  # ✅ Use transaction manager for connection

    def get_cursor(self):
        """Returns the active database cursor."""
        return self.transaction_manager.get_cursor()  # ✅ Use transaction manager for cursor
    
    def add_item(self, context, data):
        """Inserts a new item into the database."""
        
        from src.database.database_query_generator import QueryGenerator
        self.query_generator = QueryGenerator(self.db_path)
        queries = self.query_generator(context).get_all_queries()
        
        primary_key = self.get_primary_key(context)

        # Remove primary key from insert data
        insert_data = {k: v for k, v in data.items() if k != primary_key}

        if DEBUG:
            print(f"Executing Insert: {queries['insert_query']} with {insert_data}")

        return self.db_executor.execute_query(queries["insert_query"], insert_data)

    def update_item(self, context, data):
        """Updates an existing item in the database."""
        queries = self.query_generator(context).get_all_queries()

        if DEBUG:
            print(f"Executing Update: {queries['update_query']} with {data}")

        return self.db_executor.execute_query(queries["update_query"], data)

    def delete_item(self, context, item_id):
        """Deletes an item from the database."""
        queries = self.query_generator(context).get_all_queries()

        if DEBUG:
            print(f"Executing Delete: {queries['delete_query']} with ID={item_id}")

        return self.db_executor.execute_query(queries["delete_query"], {"id": item_id})



    # ✅ Import inside methods to avoid circular dependency
    def get_query_generator(context_name):
        from src.database.database_query_generator import QueryGenerator  # ✅ Local import
        return QueryGenerator(context_name, self)
