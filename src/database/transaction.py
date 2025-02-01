# Read, write, update, and delete operations.

from core.database.connection import DatabaseConnection

class DatabaseTransactionManager:
    """ Handles database transactions while ensuring connection tracking. """

    def __init__(self):
        """ Initializes the transaction manager with a shared database connection. """
        self.db = DatabaseConnection()  # ✅ Use shared DatabaseConnection
        self.connection = self.db.connection
        self.cursor = self.db.cursor
        self.connection_tracker = self.db.connection_tracker  # ✅ Ensure connections are tracked

    def begin_transaction(self):
        """ Begins a database transaction. """
        self.connection.execute("BEGIN TRANSACTION;")
        self.connection_tracker.add_connection(self.connection)  # ✅ Track the transaction connection

    def commit_transaction(self):
        """ Commits the current transaction. """
        self.connection.commit()
        self.connection_tracker.remove_connection(self.connection)  # ✅ Remove from tracker

    def rollback_transaction(self):
        """ Rolls back the current transaction. """
        self.connection.rollback()
        self.connection_tracker.remove_connection(self.connection)  # ✅ Ensure rollback is tracked

    def close(self):
        """ Closes the transaction and ensures cleanup. """
        self.cursor.close()
        self.connection.close()
        self.connection_tracker.remove_connection(self.connection)  # ✅ Cleanup connection
