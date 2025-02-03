import sys
import os
import sqlite3
import logging

from config.config_data import DATABASE_PATH

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.database_connection import DatabaseConnection  # ✅ Ensure this class exists
from src.database.connection_tracker import ConnectionTracker  # ✅ Ensure this class exists

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
        self.connection = None 
        self.connection_tracker = ConnectionTracker()  # ✅ Track active connections
        self.cursor = None
        self.connections = []

    def open_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.connection_tracker.add_connection(self.connection)  # ✅ Track the connection
            self.connections.append(self.connection)
            logger.debug("Database connection opened.")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def get_cursor(self):
        self.open_connection()
        return self.cursor
    
    def get_connection(self):
        self.open_connection()
        return self.connection
        
    def begin_transaction(self):
        self.open_connection()
        self.connection.execute("BEGIN TRANSACTION;")
        logger.debug("Transaction started.")

    def commit_transaction(self):
        if self.connection:
            self.connection.commit()
            logger.debug("Transaction committed.")
            self.connection_tracker.remove_connection(self.connection)  # ✅ Remove from tracker
        else:
            logger.warning("No active transaction to commit.")

    def rollback_transaction(self):
        if self.connection:
            self.connection.rollback()
            logger.debug("Transaction rolled back.")
            self.connection_tracker.remove_connection(self.connection)  # ✅ Ensure rollback is tracked
        else:
            logger.warning("No active transaction to roll back.")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.connection_tracker.remove_connection(self.connection)  # ✅ Cleanup connection
            logger.debug("Database connection closed.")

    def close_all_connections(self):
        for conn in self.connections:
            conn.close()
        self.connections = []
        logger.debug("✅ All database connections closed.")
