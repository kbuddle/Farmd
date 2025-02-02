import sqlite3
from config.config_data import DATABASE_PATH

class DatabaseOperations:
    """Handles all database transactions (CRUD operations)."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    def _connect(self):
        """Creates a database connection."""
        return sqlite3.connect(self.db_path)

    def fetch_all(self, table_name):
        """Fetches all items from the table."""
        query = f"SELECT * FROM {table_name}"
        with self._connect() as conn:
            return conn.execute(query).fetchall()

    def add_item(self, table_name, data):
        """Inserts an item into the specified table."""
        try:
            with self._connect() as conn:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                return cursor.lastrowid  # Return inserted row ID
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return -1  # Return error code

    def update_item(self, table_name, item_id, data):
        """Updates an item in the database."""
        try:
            with self._connect() as conn:
                set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
                query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

                conn.execute(query, tuple(data.values()) + (item_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def clone_item(self, table_name, item_id):
        """Clones an existing item in the database."""
        with self._connect() as conn:
            query = f"INSERT INTO {table_name} ({', '.join(data.keys())}) SELECT {', '.join(data.keys())} FROM {table_name} WHERE id = ?"
            cursor = conn.execute(query, (item_id,))
            conn.commit()
            return cursor.lastrowid

    def delete_item(self, table_name, item_id):
        """Deletes an item from the database."""
        try:
            with self._connect() as conn:
                query = f"DELETE FROM {table_name} WHERE id = ?"
                conn.execute(query, (item_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
