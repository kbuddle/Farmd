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
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(f"Database error: {e}")
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
