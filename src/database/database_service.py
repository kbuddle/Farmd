import sqlite3
import logging
from config.config_data import DATABASE_PATH, COLUMN_DEFINITIONS
from src.database.database_manager import DatabaseManager
from src.database.query_generator import QueryGenerator

logger = logging.getLogger(__name__)
dp_path = DATABASE_PATH

class DatabaseService:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_manager = DatabaseManager(db_path)

    def add_item(self, context, data):
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        insert_query, params = query_generator.generate_insert_query(data)
        return self.db_manager.execute_query(insert_query, params)

    def update_item(self, context, data):
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        update_query, params = query_generator.generate_update_query(data)
        return self.db_manager.execute_query(update_query, params)

    def delete_item(self, context, item_id):
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        delete_query, params = query_generator.generate_delete_query()
        return self.db_manager.execute_query(delete_query, (item_id,))

    def fetch_all(self, context):
        """Fetch all records from a given table."""
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        fetch_query = query_generator.generate_fetch_query()
        print(f"This is the fetch_query: {fetch_query}")
        results = self.db_manager.execute_query(fetch_query)
        
        # Ensure proper mapping to column names
        column_names = [desc[0] for desc in self.db_manager.cursor.description]  
        return [dict(zip(column_names, row)) for row in results]
            
    def get_primary_key(self, context):
        """Retrieves the primary key column for a given table context."""
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})

        primary_key = next(
            (col for col, details in column_definitions.items() if details.get("is_primary_key", False)), 
            None
        )

        if not primary_key:
            logger.warning(f"⚠️ No primary key defined for context: {context}")

        return primary_key
