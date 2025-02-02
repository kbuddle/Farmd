from config.config_data import COLUMN_DEFINITIONS

class DatabaseSchema:
    """ Handles fetching and processing column definitions. """

    @staticmethod
    def fetch_column_definitions(table_name):
        """ Fetches column definitions for a given table. """
        return COLUMN_DEFINITIONS.get(table_name, {}).get("columns", {})

    @staticmethod
    def process_column_definitions(context):
        """ Filters out admin-only columns. """
        columns = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})
        return {col: details for col, details in columns.items() if not details.get("admin", False)}

    @staticmethod
    def get_processed_column_definitions(column_definitions, exclude_hidden=True):
        """ Filters column definitions based on visibility settings. """
        if not isinstance(column_definitions, dict):
            raise TypeError(f"Expected dictionary for column definitions, got {type(column_definitions).__name__}")

        return {
            col: details for col, details in column_definitions.items()
            if details.get("is_primary_key", False) or not (exclude_hidden and details.get("admin", False))
        }

