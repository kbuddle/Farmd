class UIController:
    """Handles UI interactions and connects UI events with the DataManager."""

    def __init__(self, data_manager):
        """Initializes UIController with DataManager."""
        self.data_manager = data_manager

    def on_save(self, context, form_data, is_add):
        """
        Handles the save operation for the data entry form.

        Args:
            context (str): Table name.
            form_data (dict): Data collected from the form.
            is_add (bool): True for add, False for edit.
        """
        result = self.data_manager.save_data(context, form_data, is_add)

        if result:
            print(f"✅ {context} record saved successfully!")
        else:
            print(f"❌ Error saving {context} record.")

    def on_delete(self, context, item_id):
        """
        Handles deleting an item.

        Args:
            context (str): Table name.
            item_id (int): ID of the item to delete.
        """
        result = self.data_manager.delete_data(context, item_id)

        if result:
            print(f"✅ {context} record deleted successfully!")
        else:
            print(f"❌ Error deleting {context} record.")
