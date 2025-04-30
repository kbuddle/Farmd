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
        """Generates an SQL INSERT statement dynamically."""
        columns = list(data.keys())  # ✅ Explicitly converts to list
        values_placeholders = ", ".join(["?" for _ in columns])
        insert_statement = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({values_placeholders})"
        params = list(data.values())  # ✅ Ensures correct values are passed

        return insert_statement, params


    def generate_update_query(self, data):
        """Generates an SQL UPDATE statement dynamically."""
        columns_to_update = [f"{col} = ?" for col in data.keys()]
        update_statement = f"UPDATE {self.table_name} SET {', '.join(columns_to_update)} WHERE {self.primary_key} = ?"
        params = list(data.values())  # ✅ Exclude primary key from updates

        return update_statement, params

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
