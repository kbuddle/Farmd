import sqlite3
from config.config_data import DATABASE_PATH

class ConnectionTracker:
    def __init__(self):
        self.open_connections = []

    def add_connection(self, connection):
        self.open_connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.open_connections:
            self.open_connections.remove(connection)

    def force_close_all(self):
        for conn in self.open_connections.copy():
            conn.close()
            self.remove_connection(conn)