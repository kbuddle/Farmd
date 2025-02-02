# subject to redistribution within new filing structure.

from config.config_data import DATABASE_PATH
from src.models.item import Item  # ✅ Corrected import
from src.database.queries import DatabaseQueryExecutor  # ✅ Use transaction manager instance
from src.forms.validation import validate_field  # ✅ Import validation function

VALID_PROCUREMENT_TYPES = {"Purchase", "Make", "Hybrid"}

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
        - If all assigned parts are 'Make', it sets to 'Make'.
        - If at least one part is 'Make' and others are 'Purchase', it sets to 'Hybrid'.
        - If all parts are 'Purchase' or there are no parts, it sets to 'Purchase'.
        """
        query = """
            SELECT DISTINCT p.ProcurementType
            FROM Assemblies_Parts ap
            JOIN Parts p ON ap.PartID = p.PartID
            WHERE ap.ID = ?
        """
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

        # Update the database with the new ProcurementType
        update_query = """
            UPDATE Assemblies SET ProcurementType = ? WHERE AssemblyID = ?
        """
        db_manager.execute_non_query(update_query, (self.procurement_type, self.item_id), commit=True)

        print(f"DEBUG: Assembly {self.name} updated to ProcurementType: {self.procurement_type}")

    def add_part(self, part, quantity):
        """
        Assigns a part to this assembly and updates procurement type.

        :param part: Part object
        :param quantity: Quantity of the part
        """
        entity_type = "Part"  # ✅ Assign a default entity type

        # ✅ Ensure `procurement_type` exists before validation
        if not hasattr(part, "procurement_type") or part.procurement_type is None:
            print(f"WARNING: {part.name} is missing a valid ProcurementType. Defaulting to 'Purchase'.")
            part.procurement_type = "Purchase"  # ✅ Assign default before validation

        # ✅ Validate ProcurementType using `validate_field()`
        part.procurement_type = validate_field(
            "ProcurementType", 
            part.procurement_type, 
            "text",  # Treat as text type
            valid_values=VALID_PROCUREMENT_TYPES, 
            default="Purchase"
        )

        # ✅ Debugging Output: Log before inserting into the database
        print(f"DEBUG: Inserting into Assemblies_Parts - Part: {part.name}, ProcurementType: {part.procurement_type}, ID: {self.item_id}, PartID: {part.item_id}, Quantity: {quantity}, EntityType: {entity_type}")

        check_query = "SELECT ID FROM Assemblies_Parts WHERE ParentAssemblyID = ? AND PartID = ?"
        result = db_manager.execute_query(check_query, (self.item_id, part.item_id))

        if result:
            update_query = """
                UPDATE Assemblies_Parts 
                SET Quantity = Quantity + CAST(? as NUMERIC)
                WHERE ParentAssemblyID = ? AND PartID = ?
            """
            print(f"DEBUG: Running UPDATE query: {update_query} with params ({quantity}, {self.item_id}, {part.item_id})")
            db_manager.execute_non_query(update_query, (quantity, self.item_id, part.item_id), commit=True)
            print(f"✅ SUCCESS: Updated Quantity for Part {part.item_id} in Assembly {self.item_id}")

        else:
            insert_query = """
                INSERT INTO Assemblies_Parts (ProcurementType, ParentAssemblyID, ChildAssemblyID, PartID, Quantity, EntityType)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (part.procurement_type, self.item_id, self.item_id, part.item_id, quantity, entity_type)
            print(f"DEBUG: Running INSERT query: {insert_query} with params {params}")
            db_manager.execute_non_query(insert_query, params, commit=True)
            print(f"✅ SUCCESS: Added Part {part.item_id} to Assembly {self.item_id}")

    def list_parts(self):
        """Fetches all parts assigned to this assembly from the database."""
        query = """
            SELECT p.PartName, ap.Quantity
            FROM Assemblies_Parts ap
            JOIN Parts p ON ap.PartID = p.PartID
            WHERE ap.ID = ?
        """
        result = db_manager.execute_query(query, (self.item_id,))

        if not result:
            return []  # Return empty list if no parts found

        return [(row["PartName"], row["Quantity"]) for row in result]
    
    def add_parts_to_assembly(assembly_id, part_ids):
        """
        Adds selected parts to the specified assembly.

        Args:
            assembly_id (int): The ID of the selected assembly.
            part_ids (list): List of selected PartIDs to add.
        """
        for part_id in part_ids:
            print(f"DEBUG: Adding PartID {part_id} to Assembly {assembly_id}")

            insert_query = """
                INSERT INTO Assemblies_Parts (ParentAssemblyID, PartID, Quantity, EntityType)
                VALUES (?, ?, ?, ?)
            """
            db_manager.execute_non_query(insert_query, (assembly_id, part_id, 1, "Part"), commit=True)

        print(f"DEBUG: Successfully added parts {part_ids} to Assembly {assembly_id}.")
