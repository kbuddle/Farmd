import sqlite3
from config.config_data import DATABASE_PATH
from src.database.connection_tracker import ConnectionTracker

class DatabaseConnection:
    """ Singleton class to manage the database connection. """
    _instance = None

    def __new__(cls, db_path=DATABASE_PATH):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._init(db_path)
        return cls._instance

    def _init(self, db_path):
        self.db_path = db_path
        self.connection_tracker = ConnectionTracker()  # ✅ Connection tracking
        self.connection = sqlite3.connect(self.db_path, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.connection_tracker.add_connection(self.connection)

    def close(self):
        """ Closes the database connection and removes it from the tracker. """
        self.cursor.close()
        self.connection.close()
        self.connection_tracker.remove_connection(self.connection)
        DatabaseConnection._instance = None

