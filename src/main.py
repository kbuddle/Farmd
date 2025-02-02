import sys
import os
import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button
from src.ui.ui_components import create_assemblies_screen
from src.ui.ui_events import on_assembly_selection
from config.config_data import DEBUG, DATABASE_PATH
from src.database.transaction import DatabaseTransactionManager
from src.database.utils import DatabaseUtils
from src.database.operations import DatabaseOperations
from src.database.connection import DatabaseConnection
from src.ui.ui_components import ScrollableFrame  
from src.database.tracker import ConnectionTracker
from src.database.DatabaseManager import DatabaseManager
from src.core.data_manager import DataManager
from src.ui.ui_controller import UIController

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

db_manager = DatabaseManager()
data_manager = DataManager(db_manager)
ui_controller = UIController(data_manager)


db_instance = DatabaseConnection()
db_manager = DatabaseTransactionManager()
db_utils = DatabaseUtils(db_manager)
db_operations = DatabaseOperations(db_manager)

def cleanup():
    db_instance.connection_tracker.force_close_all()

atexit.register(cleanup)

def show_landing_page(root, main_container):
    """Displays the main landing page with navigation buttons."""
    for widget in main_container.winfo_children():
        widget.destroy()

    landing_frame = Frame(main_container)
    landing_frame.pack(expand=True)

    Button(landing_frame, text="Assemblies", command=lambda: show_assemblies(root, main_container)).pack(pady=10)
    Button(landing_frame, text="Parts", command=lambda: show_parts(root, main_container)).pack(pady=10)
    Button(landing_frame, text="Suppliers", command=lambda: show_suppliers(root, main_container)).pack(pady=10)
    Button(landing_frame, text="Drawings", command=lambda: show_drawings(root, main_container)).pack(pady=10)
    Button(landing_frame, text="Images", command=lambda: show_images(root, main_container)).pack(pady=10)
    
    Button(landing_frame, text="Exit", command=root.quit).pack(pady=20)

def show_assemblies(root, main_container):
    """Loads the Assemblies module dynamically."""
    for widget in main_container.winfo_children():
        widget.destroy()

    assemblies_container = Frame(main_container)
    assemblies_container.pack(fill="both", expand=True)

    card_frame = Frame(assemblies_container, relief="sunken", borderwidth=2)
    card_frame.pack(fill="x", expand=True, padx=5, pady=5)

    parts_container = Frame(main_container, relief="ridge", borderwidth=2)
    parts_container.pack(fill="both", expand=True)

    assemblies_frame, assemblies_table = create_assemblies_screen(assemblies_container)
    assemblies_table.bind("<<TreeviewSelect>>", lambda event: on_assembly_selection(event, assemblies_table, card_frame, parts_container))

    Button(assemblies_container, text="Back to Main", command=lambda: show_landing_page(root, main_container)).pack(pady=10)

def show_parts(root, main_container):
    """Placeholder function for Parts module."""
    for widget in main_container.winfo_children():
        widget.destroy()

    frame = Frame(main_container)
    frame.pack(expand=True)

    Button(frame, text="Back to Main", command=lambda: show_landing_page(root, main_container)).pack()

def show_suppliers(root, main_container):
    """Placeholder function for Suppliers module."""
    for widget in main_container.winfo_children():
        widget.destroy()

    frame = Frame(main_container)
    frame.pack(expand=True)

    Button(frame, text="Back to Main", command=lambda: show_landing_page(root, main_container)).pack()

def show_drawings(root, main_container):
    """Placeholder function for Drawings module."""
    for widget in main_container.winfo_children():
        widget.destroy()

    frame = Frame(main_container)
    frame.pack(expand=True)

    Button(frame, text="Back to Main", command=lambda: show_landing_page(root, main_container)).pack()

def show_images(root, main_container):
    """Placeholder function for Images module."""
    for widget in main_container.winfo_children():
        widget.destroy()

    frame = Frame(main_container)
    frame.pack(expand=True)

    Button(frame, text="Back to Main", command=lambda: show_landing_page(root, main_container)).pack()

def main(test_mode=False):
    """Main function controlling UI and test execution."""
    
    if test_mode:
        print("\n🔍 Running OOP Test...\n")

    root = Tk()
    root.title("FarmBot Management")
    root.geometry("1000x600")
    root.resizable(True, True)

    main_container = ScrollableFrame(root)
    main_container.pack(fill="both", expand=True)

    show_landing_page(root, main_container)

    root.mainloop()

if __name__ == "__main__":
    main(test_mode=DEBUG)
