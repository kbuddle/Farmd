from src.models.item import Part, Assembly, Supplier

class DataManager:
    """Handles business logic for saving, updating, and deleting data through UI interactions."""

    def __init__(self, db_service):
        """Initializes the DataManager with a database service."""
        self.db_service = db_service

    def fetch_all_parts(self):
        part = Part(self.db_service)
        return part.fetch_all()

    def fetch_all_assemblies(self):
        assembly = Assembly(self.db_service)
        return assembly.fetch_all()

    def fetch_all_suppliers(self):
        supplier = Supplier(self.db_service)
        return supplier.fetch_all()

    def save_data(self, context, form_data, is_add):
        """
        Saves data for add/edit operations.

        Args:
            context (str): Table name.
            form_data (dict): Data collected from the form.
            is_add (bool): True for add, False for edit.
        """
        if is_add:
            return self.db_service.add_item(context, form_data)
        else:
            return self.db_service.update_item(context, form_data)

    def delete_data(self, context, item_id):
        """Deletes an item from the database."""
        return self.db_service.delete_item(context, item_id)
