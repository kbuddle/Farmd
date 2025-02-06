# subject to redistribution within new filing structure.

from config.config_data import DATABASE_PATH
from models.item import Item 
from database.database_manager import DatabaseManager


class Part(Item):
    def __init__(self, part_id, name, procurement_type="Purchase"):
        """
        Represents a Part.

        :param part_id: Unique identifier for the part
        :param name: Name of the part
        :param procurement_type: "Purchase" (default) or "Make"
        """
        super().__init__(db_service, table_name="Parts", primary_key="PartID")
        self.item_id = part_id
        self.name = name
        self.procurement_type = procurement_type if procurement_type else "Purchase"
        
    @classmethod
    def fetch_from_db(cls, part_id):
        """Fetch a Part from the database."""
        query = "SELECT PartID, PartName, ProcurementType FROM Parts WHERE PartID = ?"
        db_manager = DatabaseManager()
        result = db_manager.execute_query(query, (part_id,))

        if result:
            return cls(result[0]["PartID"], result[0]["PartName"], result[0]["ProcurementType"])
        return None  # ✅ Return `None` if no record is found


    def save_to_db(self):
        """Save or update a Part in the database."""
        query = """
            INSERT INTO Parts (PartID, PartName, ProcurementType)
            VALUES (?, ?, ?)
            ON CONFLICT(PartID) DO UPDATE SET 
                PartName = excluded.PartName,
                ProcurementType = excluded.ProcurementType
        """
        db_manager = DatabaseManager()
        db_manager.execute_query(query, (self.item_id, self.name, self.procurement_type), commit=True)

