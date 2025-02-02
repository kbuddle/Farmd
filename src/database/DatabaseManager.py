import sqlite3
from config.config_data import DATABASE_PATH, DEBUG, COLUMN_DEFINITIONS
from src.database.transaction import DatabaseTransactionManager
from src.database.query_generator import QueryGenerator

class DatabaseManager:
    """Manages all database operations (CRUD) in an OOP approach."""

    def __init__(self, db_path=DATABASE_PATH):
        """Initializes the database manager with a connection and executor."""
        self.db_manager = DatabaseTransactionManager()  # ✅ Corrected: Removed db_path
        self.query_generator = QueryGenerator

    def add_item(self, context, data):
        """Inserts a new item into the database."""
        queries = QueryGenerator(context).get_all_queries()
        primary_key = self._get_primary_key(context)

        # Remove primary key from insert data
        insert_data = {k: v for k, v in data.items() if k != primary_key}

        if DEBUG:
            print(f"Executing Insert: {queries['insert_query']} with {insert_data}")

        return self.db_executor.execute_query(queries["insert_query"], insert_data)

    def update_item(self, context, data):
        """Updates an existing item in the database."""
        queries = QueryGenerator(context).get_all_queries()

        if DEBUG:
            print(f"Executing Update: {queries['update_query']} with {data}")

        return self.db_executor.execute_query(queries["update_query"], data)

    def delete_item(self, context, item_id):
        """Deletes an item from the database."""
        queries = QueryGenerator(context).get_all_queries()

        if DEBUG:
            print(f"Executing Delete: {queries['delete_query']} with ID={item_id}")

        return self.db_executor.execute_query(queries["delete_query"], {"id": item_id})

    def _get_primary_key(self, context):
        """Retrieves the primary key column for a given table context."""
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        return next((col for col, details in column_definitions.items() if details.get("is_primary_key", False)), None)
