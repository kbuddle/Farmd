from src.database.queries import DatabaseQueryExecutor
from config.config_data import DATABASE_PATH

class AssemblyPartsFetcher:
    """
    A class to fetch available parts and assemblies that are not assigned to a given assembly.
    """

    def __init__(self, db_manager):
        """
        Initializes the AssemblyPartsFetcher with a database connection.
        
        Args:
            db_path (str): The path to the database.
        """
        self.db_query_executor = DatabaseQueryExecutor()

    def fetch_available_items(self, assembly_id):
        """
        Fetches all available parts and assemblies that are not yet assigned to the given assembly.

        Args:
            assembly_id (int): The ID of the assembly.

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
            WHERE ap.PartID = Parts.PartID AND ap.AssemblyID = ?
        )
        UNION ALL
        SELECT AssemblyID AS ID, AssemName AS Name, 'Assembly' AS EntityType, 
               'N/A' AS Dimensions, 'N/A' AS Model, 'N/A' AS Make, 
               'N/A' AS Manufacturer, 'N/A' AS ManPartNum, 
               NULL AS PartWeight, 'N/A' AS PartMaterial, 'N/A' AS ProcurementType
        FROM Assemblies
        WHERE NOT EXISTS (
            SELECT 1 FROM Assemblies_Parts ap 
            WHERE ap.AssemblyID = Assemblies.AssemblyID AND ap.AssemblyID = ?
        );
        """

        return self.db_query_executor.execute_query(query, (assembly_id, assembly_id))

