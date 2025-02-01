# subject to redistribution within new filing structure.

from config.config_data import DATABASE_PATH
from src.models.item import Item  # ✅ Corrected import
from src.core.database_transactions import db_manager


class Part(Item):
    def __init__(self, part_id, name, procurement_type="Purchase"):
        """
        Represents a Part.

        :param part_id: Unique identifier for the part
        :param name: Name of the part
        :param procurement_type: "Purchase" (default) or "Make"
        """
        super().__init__(part_id, name)
        self.procurement_type = procurement_type
        self.procurement_type = procurement_type if procurement_type else "Purchase"  # ✅ Ensure it is always set

    @classmethod
    def fetch_from_db(cls, part_id):
        """Fetch a part using DatabaseTransactionManagement."""
        query = "SELECT PartID, PartName, ProcurementType FROM Parts WHERE PartID = ?"
        result = db_manager.execute_query(query, (part_id,))

        if result:
            return cls(result[0]["PartID"], result[0]["PartName"], result[0]["ProcurementType"])
        return None  # ✅ Return `None` if no record is found

    def save_to_db(self):
        """Save or update a Part using DatabaseTransactionManagement."""
        check_query = "SELECT COUNT(*) as count FROM Parts WHERE PartID = ?"
        result = db_manager.execute_query(check_query, (self.item_id,))

        if result and result[0]["count"] > 0:
            update_query = """
                UPDATE Parts SET PartName = ?, ProcurementType = ? WHERE PartID = ?
            """
            db_manager.execute_non_query(update_query, (self.name, self.procurement_type, self.item_id), commit=True)
        else:
            insert_query = """
                INSERT INTO Parts (PartID, PartName, ProcurementType) VALUES (?, ?, ?)
            """
            db_manager.execute_non_query(insert_query, (self.item_id, self.name, self.procurement_type), commit=True)
