# subject to redistribution within new filing structure.

import sys
import os

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add project root to sys.path
sys.path.insert(0, PROJECT_ROOT)

# Now, import your module
from src.core.database_transactions import db_manager

def test_database_operations():
    print("===== Running Database Tests =====")
    try:
        # Create a test table
        db_manager.execute_non_query("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")

        # Insert a test row
        db_manager.execute_non_query("INSERT INTO test_table (name) VALUES (:name)", {"name": "Test Entry"})

        # Fetch the row
        results = db_manager.execute_query("SELECT * FROM test_table")
        print(f"DEBUG: Retrieved Data - {results}")

        # Clean up
        db_manager.execute_non_query("DROP TABLE test_table")
    except Exception as e:
        print(f"DEBUG: Test failed: {e}")
    finally:
        db_manager.connection_tracker.force_close_all()

if __name__ == "__main__":
    test_database_operations()