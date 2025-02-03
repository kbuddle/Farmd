import sqlite3
import logging
from config.config_data import DATABASE_PATH, DEBUG, COLUMN_DEFINITIONS
from src.database.database_transaction_manager import DatabaseTransactionManager
from src.database.database_query_executor import DatabaseQueryExecutor
from src.database.database_manager import DatabaseManager 
from src.database.database_query_generator import QueryGenerator

logger = logging.getLogger(__name__)
dp_path = DATABASE_PATH

class DatabaseService:
    def __init__(self, db_path):
        self.db_transaction_manager = DatabaseTransactionManager(db_path)
        self.query_executor = DatabaseQueryExecutor(self.db_transaction_manager)

    def add_item(self, context, data):
        query_generator = QueryGenerator(context, self.db_transaction_manager)
        insert_query, params = query_generator.generate_insert_query(data)
        self.query_executor.execute_query(insert_query, params)

    def update_item(self, context, data, item_id):
        query_generator = QueryGenerator(context, self.db_transaction_manager)
        update_query, params = query_generator.generate_update_query(data, item_id)
        self.query_executor.execute_query(update_query, params)

    def delete_item(self, context, item_id):
        query_generator = QueryGenerator(context, self.db_transaction_manager)
        delete_query, params = query_generator.generate_delete_query(item_id)
        self.query_executor.execute_query(delete_query, params)

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
