from src.database.database_transaction import DatabaseTransactionManager
from config.config_data import DEBUG, COLUMN_DEFINITIONS, DATABASE_PATH
from src.database.query_generator import QueryGenerator

class DataManager:
    """Handles database save operations for adding and editing records."""

    def __init__(self, db_path=DATABASE_PATH):
        """
        Initializes the DataManager with a database transaction manager.

        Args:
            db_path (str): The path to the database file.
        """
        self.db_query_executor = DatabaseTransactionManager()  # ✅ Instantiate the missing executor
        self.query_generator = QueryGenerator

    def save_data(self, context, data, is_add):
        """
        Saves data to the database for add or edit operations.

        Args:
            context (str): The context/table name.
            data (dict): The data to save.
            is_add (bool): Whether this is an add or edit operation.
        """
        # Generate queries for the context
        queries = self.query_generator(context).get_all_queries()

        # Fetch primary key
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        primary_key = next(
            col for col, details in column_definitions.items() if details.get("is_primary_key", False)
        )

        if is_add:
            # Use the insert query, excluding the primary key
            query = queries["insert_query"]
            params = {k: v for k, v in data.items() if k != primary_key}
        else:
            # Use the update query, including the primary key
            query = queries["update_query"]
            params = data  # Include everything, including the primary key

        if DEBUG:
            print(f"Executing query: {query}")
            print(f"With params: {params}")

        # Execute the query
        self.db_query_executor.execute_query(query, params)

# ✅ Create an instance of DataManager
data_manager = DataManager()

def on_save(context, form_data, is_add):
    """
    Handles the save operation for the data entry form.

    Args:
        context (str): The context/table name.
        form_data (dict): Data collected from the form.
        is_add (bool): Whether this is a new record (add) or an edit.
    """
    data_manager.save_data(context, form_data, is_add)
