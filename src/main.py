# subject to redistribution within new filing structure.

import sys
import os
import atexit
import tkinter as tk
from tkinter import Tk, Frame
#from src.models.part import Part
#from src.models.assembly import Assembly
from src.ui.ui_components import create_assemblies_table
from src.ui.ui_events import on_assembly_selection
from config.config_data import DEBUG, DATABASE_PATH
from src.database.transaction import DatabaseTransactionManager
from src.database.utils import DatabaseUtils
from src.database.operations import DatabaseOperations
from src.database.connection import DatabaseConnection
from src.ui.ui_components import ScrollableFrame  # Import UI component
from src.database.tracker import ConnectionTracker


# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

db_instance=DatabaseConnection()

# Initialize db_manager once
db_manager = DatabaseTransactionManager()

# Pass db_manager to all components that need it
db_utils = DatabaseUtils(db_manager)
db_operations = DatabaseOperations(db_manager)

# Force cleanup of all connections on application exit
def cleanup():
    db_instance.connection_tracker.force_close_all()

atexit.register(cleanup)

def main(test_mode=False):
    """Main function controlling UI and test execution."""
    
    if test_mode:
        print("\n🔍 Running OOP Test...\n")

    # Initialize Tkinter root window
    root = Tk()
    root.title("FarmBot Management")
    root.geometry("1000x600")
    root.resizable(True, True)

    # ✅ Main container for everything
    main_container = ScrollableFrame(root)
    main_container.pack(fill="both", expand=True)

    # ✅ Frame for assemblies list and card view (upper section)
    assemblies_container = Frame(main_container, name="assemblies_container")
    assemblies_container.pack(fill="x", expand=True)

    # ✅ Frame for the card view (detailed assembly info)
    card_frame = Frame(assemblies_container, name="card_frame", relief="sunken", borderwidth=2)
    card_frame.pack(fill="x", expand=True, padx=5, pady=5)

    # ✅ Frame for assigned parts (lower section)
    parts_container = Frame(main_container, name="parts_container", relief="ridge", borderwidth=2)
    parts_container.pack(fill="both", expand=True)

    # ✅ Create Assemblies table inside the assemblies container
    assemblies_frame, assemblies_table = create_assemblies_table(assemblies_container)

    # ✅ Bind selection event to update both card view and assigned parts
    assemblies_table.bind("<<TreeviewSelect>>", lambda event: on_assembly_selection(event, assemblies_table, card_frame, parts_container))

    print("✅ DEBUG: UI frames initialized and selection event bound.")

    # Start the UI loop
    root.mainloop()

if __name__ == "__main__":
    main(test_mode=DEBUG)

