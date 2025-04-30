import tkinter as tk
from tkinter import ttk, Tk
from database.database_manager import DatabaseManager
from config.config_data import VIEW_DEFINITIONS, get_ap3_field_mapping

class AssemblyPartsFetcher:
    def __init__(self, db_service):
        self.db_manager = DatabaseManager()
        self.view_definition = VIEW_DEFINITIONS.get("AP3", {})
        self.column_mapping = get_ap3_field_mapping()
        self.columns = list(self.column_mapping.keys())
        
    def get_valid_columns(self):
        return {"PartID", "PartName", "EntityType", "Dimensions", "Model", "Make", "Manufacturer", "ProcurementType"}
    
    def fetch_available_items(self, assembly_id):
        columns_str = ", ".join(self.column_mapping.values())
        query = f"""
        SELECT {columns_str} FROM Parts 
        LEFT JOIN Assemblies ON 1=0  -- Ensures only Parts columns appear
        WHERE NOT EXISTS (
            SELECT 1 FROM Assemblies_Parts ap 
            WHERE ap.PartID = Parts.PartID AND ap.ParentAssemblyID = ?
        )
        UNION ALL
        SELECT {columns_str} FROM Assemblies 
        LEFT JOIN Parts ON 1=0  -- Ensures only Assemblies columns appear
        WHERE AssemblyID != ? 
        AND NOT EXISTS (
            SELECT 1 FROM Assemblies_Parts ap 
            WHERE ap.ChildAssemblyID = Assemblies.AssemblyID AND ap.ParentAssemblyID = ?
        );
        """
        return self.db_manager.execute_query(query, (assembly_id, assembly_id, assembly_id))


