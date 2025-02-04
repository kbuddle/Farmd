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
        """ Inserts a new record into the database, handling clones correctly. """
        primary_key_column = self.get_primary_key(context)

        # ✅ Ensure we do not manually insert the primary key (let SQLite auto-generate it)
        if primary_key_column in data:
            del data[primary_key_column]  

        query_generator = QueryGenerator(context, primary_key_column)

        # ✅ Generate INSERT query
        insert_query, params = query_generator.generate_insert_query(data)

        print(f"🔍 Running Insert Query for Cloning: {insert_query} with {params}")  # ✅ Debugging output

        return self.db_manager.execute_query(insert_query, params)


    def update_item(self, context, data):
        """ Updates an entity record in the database. The primary key is used to identify the record but is not updated. """
        query_generator = QueryGenerator(context, self.get_primary_key(context))

        # ✅ Get the primary key column
        primary_key_column = self.get_primary_key(context)

        # ✅ Extract the primary key value from `data`
        if primary_key_column not in data:
            raise ValueError(f"❌ Missing primary key '{primary_key_column}' in data for update.")

        primary_key_value = data.pop(primary_key_column)  # ✅ Remove primary key from `data`
        
        # ✅ Generate SQL query
        update_query, params = query_generator.generate_update_query(data)

        # ✅ Append primary key to `params` for WHERE clause
        params.append(primary_key_value)

        return self.db_manager.execute_query(update_query, params)

    def delete_item(self, context, item_id):
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        delete_query, params = query_generator.generate_delete_query()
        return self.db_manager.execute_query(delete_query, (item_id,))

    def fetch_all(self, context, item_id=None):
        """Fetch all records from a given table. If `item_id` is provided, fetch only that record."""
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        fetch_query = query_generator.generate_fetch_query()

        params = ()
        if item_id:
            fetch_query += f" WHERE {self.get_primary_key(context)} = ?"
            params = (item_id,)

        print(f"🔍 Running Query: {fetch_query} with params {params}")  # ✅ Debugging output

        results = self.db_manager.execute_query(fetch_query, params)

        if not results:
            print(f"⚠️ No results found for {context}. Returning empty list.")
            return []

        corrected_results = []
        for row in results:
            print(f"🛠️ Mapping row: {dict(row)}")  # ✅ Debugging output
            corrected_results.append(dict(row))

        #print(f"✅ Corrected Mapped Results: {corrected_results}")  # ✅ Debugging output

        return corrected_results

            
    def get_primary_key(self, context):
        """Retrieves the primary key column for a given table context."""
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})

        if not column_definitions:
            print(f"❌ No column definitions found for {context}. Check config.")
            return None  # ✅ Return None if column definitions are missing
        
        primary_key = next(
            (col for col, details in column_definitions.items() if details.get("is_primary_key", False)), 
            None
        )

        if not primary_key:
            print(f"❌ No primary key defined for context: {context}")
            return None  # ✅ Return None if no primary key exists

        print(f"✅ Found Primary Key for {context}: {primary_key}")  # ✅ Debugging output
        return primary_key