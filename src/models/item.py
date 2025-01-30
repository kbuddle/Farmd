class Item:
    def __init__(self, item_id, name):
        """
        Base class for all items.

        :param item_id: Unique identifier for the item
        :param name: Name of the item
        """
        self.item_id = item_id
        self.name = name

    def to_dict(self):
        """Converts object to dictionary (for backward compatibility)."""
        return {"id": self.item_id, "name": self.name}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.item_id}, {self.name})"
