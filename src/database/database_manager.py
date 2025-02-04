import sqlite3
import logging
from config.config_data import DATABASE_PATH, COLUMN_DEFINITIONS

class DatabaseManager:
    """
    Centralized manager for database connections, transactions, and query execution.
    """
    _instance = None

    def __new__(cls, db_path=DATABASE_PATH):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init(db_path)
        return cls._instance

    def _init(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger(__name__)

    def execute_query(self, query, params=None, commit=True):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            if commit:
                self.connection.commit()

            # ✅ Fetch results properly
            results = self.cursor.fetchall()
            if not results:
                print("⚠️ No data returned from query.")
                return []

            # ✅ Get column names first
            column_names = [desc[0] for desc in self.cursor.description] if self.cursor.description else []

            # ✅ Correctly extract values from `sqlite3.Row` objects
            mapped_results = []
            for row in results:
                mapped_row = {col: row[idx] for idx, col in enumerate(column_names)}
                mapped_results.append(mapped_row)

            #print(f"🛠️ Query Executed: {query}")  # ✅ Debugging output
            #print(f"🛠️ Actual Query Results: {mapped_results}")  # ✅ Debugging output

            return mapped_results
        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(f"❌ Database error: {e}")
            raise

    def begin_transaction(self):
        """Starts a transaction."""
        self.connection.execute("BEGIN TRANSACTION;")
        self.logger.debug("Transaction started.")

    def commit_transaction(self):
        """Commits the active transaction."""
        self.connection.commit()
        self.logger.debug("Transaction committed.")

    def rollback_transaction(self):
        """Rolls back the active transaction."""
        self.connection.rollback()
        self.logger.debug("Transaction rolled back.")

    def close(self):
        """Closes the database connection."""
        self.cursor.close()
        self.connection.close()
        DatabaseManager._instance = None

    def get_primary_key(self, context):
        """Retrieves the primary key column for a given table context."""
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        primary_key = next((col for col, details in column_definitions.items() if details.get("is_primary_key", False)), None)
        if not primary_key:
            self.logger.warning(f"⚠️ No primary key defined for context: {context}")
        return primary_key
