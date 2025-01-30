from src.models.item import Item
class Assembly(Item):
    def __init__(self, assembly_id, name, procurement_type):
        """
        Represents an Assembly, inheriting from Item.

        :param assembly_id: Unique identifier for the assembly
        :param name: Name of the assembly
        :param procurement_type: "Make", "Purchase", or "Hybrid"
        """
        super().__init__(assembly_id, name)
        self.procurement_type = procurement_type
        self.parts = []  # Stores (Part, quantity)

    def add_part(self, part, quantity):
        """
        Assigns a part to this assembly.

        :param part: Part object
        :param quantity: Quantity of the part
        """
        if self.procurement_type == "Purchase" and part.procurement_type == "Make":
            raise ValueError(f"Assembly '{self.name}' is set to 'Purchase' but contains a 'Make' part.")
        self.parts.append((part, quantity))

    def list_parts(self):
        """Returns all parts assigned to this assembly."""
        return [(p.name, qty) for p, qty in self.parts]

    def to_dict(self):
        """Converts object to dictionary (for compatibility)."""
        data = super().to_dict()
        data["procurement_type"] = self.procurement_type
        data["parts"] = [(p.to_dict(), qty) for p, qty in self.parts]
        return data
