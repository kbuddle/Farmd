from src.models.item import Item
from src.database.database_manager import DatabaseManager

VALID_PROCUREMENT_TYPES = {"Purchase", "Make", "Hybrid"}

class Assembly(Item):
    """ Represents an Assembly entity with additional procurement logic. """

    def __init__(self, db_service, assembly_id, name, procurement_type="Purchase"):
        """
        Initialize an Assembly entity.

        :param db_service: DatabaseService instance
        :param assembly_id: Unique identifier for the assembly
        :param name: Name of the assembly
        :param procurement_type: "Purchase", "Make", or "Hybrid"
        """
        super().__init__(db_service, table_name="Assemblies", primary_key="AssemblyID")
        self.item_id = assembly_id
        self.name = name
        self.procurement_type = procurement_type if procurement_type else "Purchase"

    @classmethod
    def fetch_from_db(cls, db_service, assembly_id):
        """Fetch an assembly from the database."""
        query = "SELECT AssemblyID, AssemName, ProcurementType FROM Assemblies WHERE AssemblyID = ?"
        db_manager = DatabaseManager()
        result = db_manager.execute_query(query, (assembly_id,))

        if result:
            return cls(db_service, result[0]["AssemblyID"], result[0]["AssemName"], result[0]["ProcurementType"])
        return None  # ✅ Return `None` if no record is found

    def save_to_db(self):
        """Save or update an Assembly in the database."""
        query = """
            INSERT INTO Assemblies (AssemblyID, AssemName, ProcurementType)
            VALUES (?, ?, ?)
            ON CONFLICT(AssemblyID) DO UPDATE SET 
                AssemName = excluded.AssemName,
                ProcurementType = excluded.ProcurementType
        """
        db_manager = DatabaseManager()
        db_manager.execute_query(query, (self.item_id, self.name, self.procurement_type), commit=True)

    def update_procurement_type(self):
        """Automatically updates the procurement type based on assigned components."""
        query = """
            SELECT DISTINCT p.ProcurementType
            FROM Assemblies_Parts ap
            JOIN Parts p ON ap.PartID = p.PartID
            WHERE ap.ParentAssemblyID = ?
        """
        db_manager = DatabaseManager()
        result = db_manager.execute_query(query, (self.item_id,))

        if not result:
            self.procurement_type = "Purchase"  # No parts assigned, default to Purchase
        else:
            procurement_types = {row["ProcurementType"] for row in result}

            if procurement_types == {"Make"}:
                self.procurement_type = "Make"
            elif "Make" in procurement_types:
                self.procurement_type = "Hybrid"
            else:
                self.procurement_type = "Purchase"

        update_query = "UPDATE Assemblies SET ProcurementType = ? WHERE AssemblyID = ?"
        db_manager.execute_query(update_query, (self.procurement_type, self.item_id), commit=True)

    def fetch_available_components(self):
        """Fetch only unassigned parts or assemblies."""
        query = """
            SELECT PartID, PartName FROM Parts 
            WHERE PartID NOT IN (
                SELECT PartID FROM Assemblies_Parts WHERE ParentAssemblyID = ?
            )
        """
        db_manager = DatabaseManager()
        return db_manager.execute_query(query, (self.item_id,))

    def add_part(self, part_id, quantity):
        """Assigns a part to this assembly and updates procurement type."""
        query = """
            INSERT INTO Assemblies_Parts (ParentAssemblyID, PartID, Quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(ParentAssemblyID, PartID) 
            DO UPDATE SET Quantity = Assemblies_Parts.Quantity + excluded.Quantity
        """
        db_manager = DatabaseManager()
        db_manager.execute_query(query, (self.item_id, part_id, quantity), commit=True)
        self.update_procurement_type()

    def remove_part(self, part_id):
        """Removes a part from the assembly and updates procurement type."""
        query = "DELETE FROM Assemblies_Parts WHERE ParentAssemblyID = ? AND PartID = ?"
        db_manager = DatabaseManager()
        db_manager.execute_query(query, (self.item_id, part_id), commit=True)
        self.update_procurement_type()
