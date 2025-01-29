import sqlite3
from config_data import COLUMN_DEFINITIONS, DEBUG






def refresh_column_definitions(table_name, debug=False):
    """
    Refreshes column definitions by querying the database schema.

    Args:
        table_name (str): The name of the table to refresh.

    Returns:
        dict: A dictionary of column definitions.
    """
    
    table_name="Assemblies"
    query = f"PRAGMA table_info({table_name});"
    connection = sqlite3.connect("D:\FarmbotPythonV2\Farmbot.db")
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = {
            row[1]: {
                "display_name": row[1],
                "type": row[2],
                "is_primary_key": row[5] == 1
            }
            for row in results
        }
        return columns
    finally:
        connection.close()

# Dynamically refresh column definitions for the Assemblies table
COLUMN_DEFINITIONS["Assemblies"]["columns"] = refresh_column_definitions("Assemblies")




# Dynamically refresh column definitions for the Assemblies table
COLUMN_DEFINITIONS["Assemblies"]["columns"] = refresh_column_definitions("Assemblies")

print(f"DEBUG: Updated COLUMN_DEFINITIONS for Assemblies: {COLUMN_DEFINITIONS['Assemblies']['columns']}")