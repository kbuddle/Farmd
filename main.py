import atexit
from tkinter import Tk, ttk
from ui.notebook_manager import create_datasheet_tab
from core.query_builder import query_generator
from ui.ui_helpers import placeholder_add, placeholder_build, placeholder_clone, placeholder_delete, placeholder_edit, center_window_vertically
from forms.validation import validate_contexts
from config.config_data import CONTEXTS, COLUMN_DEFINITIONS, DEBUG
from core.database_transactions import db_manager  # Import db_manager for cleanup

# Import OOP Test Code
from src.models.part import Part
from src.models.assembly import Assembly


# Force cleanup of all connections on application exit
def cleanup():
    print("DEBUG: Application exiting. Force-closing all database connections...")
    db_manager.connection_tracker.force_close_all()

# Register the cleanup function with atexit
atexit.register(cleanup)

def run_oop_test():
    """Runs a basic test for the OOP refactor."""
    # Create parts
    bolt = Part(1, "Bolt", "Purchase")
    frame = Part(2, "Frame", "Make")

    bolt.save_to_db()
    frame.save_to_db()

    # Create an assembly
    robot_arm = Assembly(1001, "Robot Arm")
    robot_arm.save_to_db()

    # Assign parts
    robot_arm.add_part(bolt, 10)  # Initially Purchase
    robot_arm.update_procurement_type()  # Should still be Purchase

    robot_arm.add_part(frame, 1)  # Now Hybrid
    robot_arm.update_procurement_type()  # Should update to Hybrid

    print(f"🔹 Updated ProcurementType for {robot_arm.name}: {robot_arm.procurement_type}")

def main(test_mode=True):
    #print("Main function started")

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
    main()
