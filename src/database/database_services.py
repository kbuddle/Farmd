import sqlite3
import logging
from config.config_data import DATABASE_PATH, DEBUG, COLUMN_DEFINITIONS
from src.database.database_transaction import DatabaseTransactionManager
from src.database.database_query_executor import DatabaseQueryExecutor
from src.database.database_manager import DatabaseManager 

logger = logging.getLogger(__name__)

class DatabaseService:
    """Handles database transactions and queries for CRUD operations."""

    def __init__(self, database_manager: DatabaseManager):
        """Initializes the database service."""
        

        self.database_manager = database_manager
        self.query_executor = DatabaseQueryExecutor(self.database_manager)
        
    def add_item(self, context, data):
        """Inserts a new record into the database."""
        from src.database.query_generator import QueryGenerator 
        
        queries = QueryGenerator(context, self.database_manager).get_all_queries()
        primary_key = self.get_primary_key(context)

        # ✅ Remove primary key from insert data
        insert_data = {k: v for k, v in data.items() if k != primary_key}

        if DEBUG:
            logger.debug(f"Executing Insert: {queries['insert_query']} with {insert_data}")

        return self.query_executor.execute_query(queries["insert_query"], insert_data)

    def update_item(self, context, item_id, updated_data):
        """Updates an existing record in the database."""
        from src.database.query_generator import QueryGenerator 
        
        queries = QueryGenerator(context, self.database_manager).get_all_queries()
        updated_data["id"] = item_id  # ✅ Ensure item ID is included

        if DEBUG:
            logger.debug(f"Executing Update: {queries['update_query']} with {updated_data}")

        return self.query_executor.execute_query(queries["update_query"], updated_data)

    def clone_item(self, context, item_id):
        """Clones an existing record by duplicating its values."""
        from src.database.query_generator import QueryGenerator 
        
        queries = QueryGenerator(context, self.database_manager).get_all_queries()

        # ✅ Correct SQL syntax for cloning (Exclude primary key)
        clone_query = f"""
        INSERT INTO {context} ({', '.join(queries['fetch_query'].split('SELECT ')[1].split(' FROM ')[0].split(', ')[1:])})
        SELECT {', '.join(queries['fetch_query'].split('SELECT ')[1].split(' FROM ')[0].split(', ')[1:])} FROM {context}
        WHERE id = :id
        """

        if DEBUG:
            logger.debug(f"Executing Clone: {clone_query} with ID={item_id}")

        return self.query_executor.execute_query(clone_query, {"id": item_id})

    def delete_item(self, context, item_id):
        """Deletes a record from the database."""
        from src.database.query_generator import QueryGenerator 
        
        queries = QueryGenerator(context, self.database_manager).get_all_queries()
        
        if DEBUG:
            logger.debug(f"Executing Delete: {queries['delete_query']} with ID={item_id}")

        return self.query_executor.execute_query(queries["delete_query"], {"id": item_id})

    def fetch_all(self, context):
        """Fetches all records from the database."""
        from src.database.query_generator import QueryGenerator
        
        queries = QueryGenerator(context, self.database_manager).get_all_queries()

        if DEBUG:
            logger.debug(f"Fetching all records for {context}")

        return self.query_executor.execute_query(queries["fetch_query"], {})

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
