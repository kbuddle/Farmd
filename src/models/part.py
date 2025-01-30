from models.item import Item

class Part(Item):
    def __init__(self, part_id, name, procurement_type="Purchase"):
        """
        Represents a Part, inheriting from Item.

        :param part_id: Unique identifier for the part
        :param name: Name of the part
        :param procurement_type: "Purchase" (default) or "Make"
        """
        super().__init__(part_id, name)
        self.procurement_type = procurement_type

    def to_dict(self):
        """Converts object to dictionary (for compatibility)."""
        data = super().to_dict()
        data["procurement_type"] = self.procurement_type
        return data
