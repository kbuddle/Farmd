 # Ensuring correct import path
from config.config_data import COLUMN_DEFINITIONS
import logging
from config.config_data import DEBUG


from src.database.database_query_executor import DatabaseQueryExecutor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class QueryGenerator:
    """
    A class to generate SQL queries dynamically based on column definitions and context (e.g., Suppliers, Assemblies).
    """

    def __init__(self, context_name, database_manager, debug=False):
        """
        Initializes the QueryGenerator with the context name and retrieves column definitions.

        Args:
            context_name (str): The name of the table or context.
            debug (bool): Whether to enable debug mode.
        """
        from src.forms.column_processor import ColumnProcessor

        self.context_name = context_name
        self.database_manager = database_manager
        self.debug = debug

        # Retrieve processed columns from ColumnProcessor
        self.processed_columns = ColumnProcessor.get_editable_columns(self.context_name)

        if not isinstance(self.processed_columns, dict):
            raise TypeError(f"'columns' for context '{self.context_name}' must be a dictionary, got {type(self.processed_columns)}")

        # ✅ Use DatabaseManager to retrieve the primary key
        from src.database.database_manager import DatabaseManager
        self.database_manager = DatabaseManager
        
        self.primary_key = self.database_manager.get_primary_key(self.context_name)

        if self.debug:
            logger.debug(f"QueryGenerator initialized for {self.context_name}")
            logger.debug(f"Primary Key: {self.primary_key}")
            logger.debug(f"Processed Columns: {self.processed_columns}")

    def generate_fetch_query(self):
        """
        Generates a SQL SELECT query for fetching records.

        Returns:
            str: The SQL SELECT query.
        """
        visible_columns = [col for col, details in self.processed_columns.items() if not details.get("admin", False)]
        query = f"SELECT {', '.join(visible_columns)} FROM {self.context_name}"

        if self.debug:
            logger.debug(f"Generated fetch query: {query}")

        return query

    def generate_insert_query(self):
        """
        Generates a SQL INSERT query.

        Returns:
            str: The SQL INSERT query.
        """
        insertable_columns = [
            col for col, details in self.processed_columns.items()
            if not details.get("admin", False) and col != self.primary_key
        ]
        query = (
            f"INSERT INTO {self.context_name} ({', '.join(insertable_columns)}) "
            f"VALUES ({', '.join(f':{col}' for col in insertable_columns)})"
        )

        if self.debug:
            logger.debug(f"Generated insert query: {query}")

        return query

    def generate_update_query(self):
        """
        Generates a SQL UPDATE query.

        Returns:
            str: The SQL UPDATE query.
        """
        updatable_columns = [
            col for col, details in self.processed_columns.items()
            if col != self.primary_key and not details.get("foreign_key", False)
        ]
        set_clause = ", ".join([f"{col} = :{col}" for col in updatable_columns])
        query = f"UPDATE {self.context_name} SET {set_clause} WHERE {self.primary_key} = :{self.primary_key}"

        if self.debug:
            logger.debug(f"Generated update query: {query}")

        return query

    def generate_delete_query(self):
        """
        Generates a SQL DELETE query.

        Returns:
            str: The SQL DELETE query.
        """
        query = f"DELETE FROM {self.context_name} WHERE {self.primary_key} = :{self.primary_key}"

        if self.debug:
            logger.debug(f"Generated delete query: {query}")

        return query

    def generate_sort_query(self, base_query, sort_column, sort_direction):
        """
        Generates a dynamic SORT query.

        Args:
            base_query (str): The base SELECT query.
            sort_column (str): The column to sort by.
            sort_direction (str): The sort direction (ASC or DESC).

        Returns:
            str: The dynamically generated SORT query.

        Raises:
            ValueError: If the sort column is invalid.
        """
        if sort_column not in self.processed_columns:
            raise ValueError(f"Invalid sort column: {sort_column}")

        query = f"{base_query} ORDER BY {sort_column} {sort_direction}"

        if self.debug:
            logger.debug(f"Generated sort query: {query}")

        return query

    def get_all_queries(self):
        """
        Returns all queries as a dictionary.

        Returns:
            dict: A dictionary with fetch, insert, update, and delete queries.
        """
        return {
            "fetch_query": self.generate_fetch_query(),
            "insert_query": self.generate_insert_query(),
            "update_query": self.generate_update_query(),
            "delete_query": self.generate_delete_query(),
        }
