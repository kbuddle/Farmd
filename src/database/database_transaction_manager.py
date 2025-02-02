import sqlite3
import logging
from src.database.database_connection import DatabaseConnection
from src.database.connection_tracker import ConnectionTracker  # ✅ Ensure this class exists
from config.config_data import DATABASE_PATH


logger = logging.getLogger(__name__)

class DatabaseTransactionManager:
    """Handles database transactions while ensuring connection tracking."""

    def __init__(self, db_path=DATABASE_PATH):
        """
        Initializes the transaction manager with a shared database connection.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection_tracker = ConnectionTracker()  # ✅ Track active connections
        self.cursor = self.connection.cursor

    def get_connection(self):
        return self.connection
    
    def get_cursor(self):
        return self.cursor
        
    def open_connection(self):
        """Opens a new database connection if not already opened."""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.connection_tracker.add_connection(self.connection)  # ✅ Track the connection

    def begin_transaction(self):
        """Begins a database transaction."""
        self.open_connection()
        self.connection.execute("BEGIN TRANSACTION;")
        logger.debug("Transaction started.")

    def commit_transaction(self):
        """Commits the current transaction."""
        if self.connection:
            self.connection.commit()
            logger.debug("Transaction committed.")
            self.connection_tracker.remove_connection(self.connection)  # ✅ Remove from tracker
        else:
            logger.warning("No active transaction to commit.")

    def rollback_transaction(self):
        """Rolls back the current transaction."""
        if self.connection:
            self.connection.rollback()
            logger.debug("Transaction rolled back.")
            self.connection_tracker.remove_connection(self.connection)  # ✅ Ensure rollback is tracked
        else:
            logger.warning("No active transaction to roll back.")

    def close(self):
        """Closes the database transaction and ensures cleanup."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.connection_tracker.remove_connection(self.connection)  # ✅ Cleanup connection
            logger.debug("Database connection closed.")

    def close_all_connections(self):
        """Closes all active database connections."""
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        logger.debug("✅ All database connections closed.")
