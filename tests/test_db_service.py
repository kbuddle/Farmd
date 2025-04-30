import sys
import os

# ✅ Ensure `src/` is in the Python path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)  # ✅ Insert at the start

# ✅ Debugging: Print the updated Python path

# ✅ Corrected import paths (Remove `` prefix)
from database.database_manager import DatabaseManager
from database.database_service import DatabaseService

# ✅ Initialize DatabaseManager and DatabaseService
db_manager = DatabaseManager("d:/FarmbotPythonV2/src/database/farmbot.db")
db_service = DatabaseService(db_manager)

# ✅ Test: Fetch all parts as dictionaries
query = "SELECT PartID, PartName FROM Parts LIMIT 5;"
results = db_service.fetch_all_dict(query)

print("Test Fetch All as Dictionary:")
for row in results:
    print(row)  # ✅ Expected: {'PartID': 1, 'PartName': 'Screw', 'EntityType': 'Part'}

# ✅ Test: Fetch a single part
query = "SELECT PartID, PartName FROM Parts WHERE PartID = ?;"
result = db_service.fetch_one_dict(query, (1,))

print("\nTest Fetch One as Dictionary:")
print(result)  # ✅ Expected: {'PartID': 1, 'PartName': 'Screw', 'EntityType': 'Part'}
