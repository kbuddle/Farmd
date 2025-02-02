class DataManager:
    """Handles business logic for saving, updating, and deleting data through UI interactions."""

    def __init__(self, db_manager):
        """Initializes the DataManager with a database manager."""
        self.db_manager = db_manager  # ✅ Use OOP-based DatabaseManager

    def save_data(self, context, form_data, is_add):
        """
        Saves data for add/edit operations.

        Args:
            context (str): Table name.
            form_data (dict): Data collected from the form.
            is_add (bool): True for add, False for edit.
        """
        if is_add:
            return self.db_manager.add_item(context, form_data)
        else:
            return self.db_manager.update_item(context, form_data)

    def delete_data(self, context, item_id):
        """Deletes an item from the database."""
        return self.db_manager.delete_item(context, item_id)
