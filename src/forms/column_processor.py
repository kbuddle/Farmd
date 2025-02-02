from config.config_data import COLUMN_DEFINITIONS
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ColumnProcessor:
    """
    A class responsible for processing column definitions from the configuration.
    """

    def __init__(self, context_name, exclude_hidden=True, debug=False):
        """
        Initializes the ColumnProcessor with the given context name.

        Args:
            context_name (str): The name of the context (e.g., "Assemblies", "Parts").
            exclude_hidden (bool): Whether to exclude hidden or admin-only columns.
            debug (bool): Enable debug logging.
        """
        self.context_name = context_name
        self.exclude_hidden = exclude_hidden
        self.debug = debug
        self.column_definitions = self._load_column_definitions()

        if self.debug:
            logger.debug(f"Initialized ColumnProcessor for '{self.context_name}' with exclude_hidden={self.exclude_hidden}")

    def _load_column_definitions(self):
        """
        Retrieves column definitions from the configuration.

        Returns:
            dict: Column definitions for the given context.
        """
        context_data = COLUMN_DEFINITIONS.get(self.context_name)

        if not context_data:
            raise ValueError(f"ERROR: No column definitions found for '{self.context_name}'.")

        if self.debug:
            logger.debug(f"Loaded column definitions for {self.context_name}: {context_data}")

        return context_data

    def get_processed_column_definitions(self):
        """
        Processes column definitions, optionally filtering out hidden/admin-only columns.

        Returns:
            dict: Processed column definitions.
        """
        if not isinstance(self.column_definitions.get("columns"), dict):
            raise TypeError(f"Expected 'columns' to be a dictionary for '{self.context_name}', got {type(self.column_definitions.get('columns'))}")

        processed_columns = {
            col: details
            for col, details in self.column_definitions["columns"].items()
            if details.get("is_primary_key", False) or not (self.exclude_hidden and details.get("admin", False))
        }

        if self.debug:
            logger.debug(f"Processed columns for '{self.context_name}': {processed_columns}")

        return processed_columns

    def get_processed_columns(self):
        """
        Retrieves processed column definitions in a structured list format.

        Returns:
            list[dict]: A list of column definitions as dictionaries.
        """
        columns_dict = self.get_processed_column_definitions()

        # Convert dict to structured list
        processed_columns_list = [{"name": key, **value} for key, value in columns_dict.items()]

        if self.debug:
            logger.debug(f"Structured column list for '{self.context_name}': {processed_columns_list}")

        return processed_columns_list

