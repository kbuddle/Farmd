import sys
import os

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can safely import models
from src.models.part import Part
from src.models.assembly import Assembly


import atexit
from tkinter import Tk, ttk
from ui.notebook_manager import create_datasheet_tab
from core.query_builder import query_generator
from ui.ui_helpers import placeholder_add, placeholder_build, placeholder_clone, placeholder_delete, placeholder_edit, center_window_vertically
from forms.validation import validate_contexts
from config.config_data import CONTEXTS, COLUMN_DEFINITIONS, DEBUG, DATABASE_PATH
from core.database_transactions import db_manager  # Import db_manager for cleanup




# Force cleanup of all connections on application exit
def cleanup():
    print("DEBUG: Application exiting. Force-closing all database connections...")
    db_manager.connection_tracker.force_close_all()

# Register the cleanup function with atexit
atexit.register(cleanup)

def run_oop_test():
    """Runs a basic test for the OOP refactor."""
    print("\n🛠️ Running OOP Test...")

    # Step 1: Create Parts
    bolt = Part(1, "Bolt", "Purchase")
    frame = Part(2, "Frame", "Make")

    # Step 2: Create an Assembly
    robot_arm = Assembly(1001, "Robot Arm", "Make")

    # Step 3: Assign Parts to the Assembly
    robot_arm.add_part(bolt, 10)  # 10 Bolts
    robot_arm.add_part(frame, 1)  # 1 Frame

    # Step 4: Output Assigned Parts
    print("🛠️ Assembly Parts List:")
    print(robot_arm.list_parts())  # Expected Output: [('Bolt', 10), ('Frame', 1)]

    # Step 5: Check Dictionary Conversion (for backward compatibility)
    print("\n🔄 Dictionary Representation:")
    print(robot_arm.to_dict())  # Expected dictionary format

    # Step 6: Test Procurement Validation (Should Raise an Error)
    try:
        purchased_assembly = Assembly(2002, "Pre-Built Kit", "Purchase")
        purchased_assembly.add_part(frame, 2)  # Trying to add a 'Make' part to a 'Purchase' assembly
    except ValueError as e:
        print("\n🚨 Error Caught as Expected:")
        print(e)

def main(test_mode=True):
    #print("Main function started")
    if test_mode:
        print("\n🔍 Running OOP Test...\n")  # Debug message to confirm execution
        run_oop_test()  # ✅ Force execution of the test

    # Define context names (list of strings)
    context_names = CONTEXTS["Some"] if test_mode else CONTEXTS["All"]
    #print(f"Contexts: {context_names}")

    # Initialize Tkinter root and notebook
    root = Tk()
    root.title("FarmBot Management")
    #print("Tkinter window initialized")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    #print("Notebook widget created")

    # Loop through the context names and fetch corresponding data
    for context_name in context_names:
        try:
            # Retrieve column definitions for the current context
            context_data = COLUMN_DEFINITIONS.get(context_name)
            if not context_data:
                raise ValueError(f"No context data found for '{context_name}'")

            # Add the 'name' key to context_data for tab display
            context_data["name"] = context_name
            #print(f"Updated context data passed to create_database_tab '{context_data}'")

            # Pass the table name (context_name) and full context_data
            create_datasheet_tab(notebook, context_name, context_data) 
            print(f"Successfully created tab for context: {context_name}")

        except Exception as e:
            print(f"Failed to create tab for context '{context_name}': {e}")

    # Run the Tkinter main event loop
    root.mainloop()

if __name__ == "__main__":
    main(test_mode=DEBUG)
