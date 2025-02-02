import sys
import os
import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button
from src.ui.ui_components import ScrollableFrame  
from src.ui.ui_events import on_assembly_selection
from src.core.service_container import ServiceContainer
from src.ui.assemblies_screen import AssembliesScreen
from config.config_data import DEBUG
from src.ui.entity_screen import EntityScreen
from src.database.datasheet_manager import DatasheetManager

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Initialize the service container
services = ServiceContainer()    

def cleanup():
    """Ensures all database connections are closed on exit."""
    services.database_service.database_manager.close_all_connections() 

atexit.register(cleanup)

# ✅ UI HANDLING SEPARATED FROM DATA OPERATIONS
class FarmBotApp:
    """Main UI controller for the FarmBot management system."""

    def __init__(self, root):
        """
        Initializes the main UI.

        Args:
            root (tk.Tk): The main application window.
        """
        self.root = root
        self.root.title("FarmBot Management")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        self.main_container = ScrollableFrame(self.root)
        self.main_container.pack(fill="both", expand=True)

        self.show_landing_page()

    def clear_main_container(self):
        """Clears all widgets in the main container before loading a new module."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_landing_page(self):
        """Displays the main landing page with navigation buttons."""
        self.clear_main_container()
        landing_frame = Frame(self.main_container)
        landing_frame.pack(expand=True)

        Button(landing_frame, text="Assemblies", command=self.show_assemblies).pack(pady=10)
        Button(landing_frame, text="Parts", command=self.show_parts).pack(pady=10)
        Button(landing_frame, text="Suppliers", command=self.show_suppliers).pack(pady=10)
        Button(landing_frame, text="Drawings", command=self.show_drawings).pack(pady=10)
        Button(landing_frame, text="Images", command=self.show_images).pack(pady=10)
        Button(landing_frame, text="Exit", command=self.root.quit).pack(pady=20)

    def show_assemblies(self):
        """Loads the Assemblies module dynamically."""
        self.clear_main_container()
        AssembliesScreen(self.main_container, self.show_landing_page)

    def show_parts(self):
        """Loads the Parts module dynamically."""
        self.clear_main_container()
        EntityScreen(self.main_container, "Parts", self.show_landing_page)
       
    def show_suppliers(self):
        """Loads the Suppliers module dynamically."""
        self.clear_main_container()
        frame = Frame(self.main_container)
        frame.pack(expand=True)
        Button(frame, text="Back to Main", command=self.show_landing_page).pack()

    def show_drawings(self):
        """Loads the Drawings module dynamically."""
        self.clear_main_container()
        frame = Frame(self.main_container)
        frame.pack(expand=True)
        Button(frame, text="Back to Main", command=self.show_landing_page).pack()

    def show_images(self):
        """Loads the Images module dynamically."""
        self.clear_main_container()
        frame = Frame(self.main_container)
        frame.pack(expand=True)
        Button(frame, text="Back to Main", command=self.show_landing_page).pack()

def main(test_mode=False):
    """Main function controlling UI and test execution."""
    
    if test_mode:
        print("\n🔍 Running OOP Test...\n")

    root = Tk()
    app = FarmBotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main(test_mode=DEBUG)
