import logging

class QueryGenerator:
    """
    Generates SQL queries dynamically based on column definitions and context.
    """
    def __init__(self, table_name, primary_key):
        self.table_name = table_name
        self.primary_key = primary_key
        self.logger = logging.getLogger(__name__)

    def generate_fetch_query(self):
        """Generates a SQL SELECT query for fetching records."""
        return f"SELECT * FROM {self.table_name}"

    def generate_insert_query(self, data):
        """Generates a SQL INSERT query."""
        columns = ", ".join(data.keys())
        values = ", ".join(["?" for _ in data.keys()])
        return f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})", tuple(data.values())

    def generate_update_query(self, data):
        """Generates a SQL UPDATE query."""
        set_clause = ", ".join([f"{col} = ?" for col in data.keys() if col != self.primary_key])
        values = tuple(data.values()) + (data[self.primary_key],)
        return f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = ?", values

    def generate_delete_query(self):
        """Generates a SQL DELETE query."""
        return f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?", (self.primary_key,)

    def get_all_queries(self, data):
        """Returns all queries as a dictionary."""
        return {
            "fetch_query": self.generate_fetch_query(),
            "insert_query": self.generate_insert_query(data),
            "update_query": self.generate_update_query(data),
            "delete_query": self.generate_delete_query(),
        }
