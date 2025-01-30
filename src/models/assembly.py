from config.config_data import DATABASE_PATH
from src.models.item import Item  # ✅ Corrected import
from core.database_transactions import db_manager  # ✅ Use transaction manager instance

class Assembly(Item):
    def __init__(self, assembly_id, name, procurement_type="Purchase"):
        """
        Represents an Assembly.

        :param assembly_id: Unique identifier for the assembly
        :param name: Name of the assembly
        :param procurement_type: "Purchase", "Make", or "Hybrid"
        """
        super().__init__(assembly_id, name)
        self.procurement_type = procurement_type

    @classmethod
    def fetch_from_db(cls, assembly_id):
        """Fetch an assembly using DatabaseTransactionManagement."""
        query = "SELECT AssemblyID, AssemName, ProcurementType FROM Assemblies WHERE AssemblyID = ?"
        result = db_manager.execute_query(query, (assembly_id,))

        if result:
            return cls(result[0]["AssemblyID"], result[0]["AssemName"], result[0]["ProcurementType"])
        return None  # ✅ Return `None` if no record is found

    def save_to_db(self):
        """Save or update an Assembly using DatabaseTransactionManagement."""
        check_query = "SELECT COUNT(*) as count FROM Assemblies WHERE AssemblyID = ?"
        result = db_manager.execute_query(check_query, (self.item_id,))

        if result and result[0]["count"] > 0:
            update_query = """
                UPDATE Assemblies SET AssemName = ?, ProcurementType = ? WHERE AssemblyID = ?
            """
            db_manager.execute_non_query(update_query, (self.name, self.procurement_type, self.item_id), commit=True)
        else:
            insert_query = """
                INSERT INTO Assemblies (AssemblyID, AssemName, ProcurementType) VALUES (?, ?, ?)
            """
            db_manager.execute_non_query(insert_query, (self.item_id, self.name, self.procurement_type), commit=True)

    def update_procurement_type(self):
        """
        Updates the procurement type of an assembly based on assigned parts.
        If all assigned parts are 'Make', it sets to 'Make'.
        If at least one part is 'Make' and the rest are 'Purchase', it sets to 'Hybrid'.
        Otherwise, it remains 'Purchase'.
        """
        query = """
            SELECT DISTINCT p.ProcurementType
            FROM Assemblies_Parts ap
            JOIN Parts p ON ap.PartID = p.PartID
            WHERE ap.AssemblyID = ?
        """
        result = db_manager.execute_query(query, (self.item_id,))

        if not result:
            return  # No parts assigned, do nothing

        procurement_types = {row["ProcurementType"] for row in result}

        if procurement_types == {"Make"}:
            self.procurement_type = "Make"
        elif "Make" in procurement_types:
            self.procurement_type = "Hybrid"
        else:
            self.procurement_type = "Purchase"

        # Update the database with the new ProcurementType
        update_query = """
            UPDATE Assemblies SET ProcurementType = ? WHERE AssemblyID = ?
        """
        db_manager.execute_non_query(update_query, (self.procurement_type, self.item_id), commit=True)
