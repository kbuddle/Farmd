from src.database.database_manager import DatabaseManager

class AssemblyPartsFetcher:
    """
    Fetches available parts and assemblies that are not yet assigned to a given assembly.
    """

    def __init__(self):
        """ Initializes database manager. """
        self.db_manager = DatabaseManager()

    def fetch_available_items(self, assembly_id):
        """
        Fetches all available parts and assemblies that are NOT assigned to the given assembly.

        Args:
            assembly_id (int): The ID of the parent assembly.

        Returns:
            list[dict]: A list of available items as dictionaries.
        """
        query = """
        SELECT PartID AS ID, PartName AS Name, 'Part' AS EntityType, 
               Dimensions, Model, Make, Manufacturer, ManPartNum, 
               PartWeight, PartMaterial, ProcurementType
        FROM Parts
        WHERE NOT EXISTS (
            SELECT 1 FROM Assemblies_Parts ap 
            WHERE ap.PartID = Parts.PartID AND ap.ParentAssemblyID = ?
        )
        UNION ALL
        SELECT AssemblyID AS ID, AssemName AS Name, 'Assembly' AS EntityType, 
               NULL AS Dimensions, NULL AS Model, NULL AS Make, 
               NULL AS Manufacturer, NULL AS ManPartNum, 
               NULL AS PartWeight, NULL AS PartMaterial, ProcurementType
        FROM Assemblies
        WHERE AssemblyID != ? 
        AND NOT EXISTS (
            SELECT 1 FROM Assemblies_Parts ap 
            WHERE ap.ChildAssemblyID = Assemblies.AssemblyID AND ap.ParentAssemblyID = ?
        );
        """

        return self.db_manager.execute_query(query, (assembly_id, assembly_id, assembly_id))
