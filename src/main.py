import sys
import os

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button
from ui.ui_components import ScrollableFrame
from ui.ui_events import on_assembly_selection
from core.service_container import ServiceContainer
from ui.assemblies_screen import AssembliesScreen
from config.config_data import DEBUG, VIEW_DEFINITION
from ui.entity_screen import EntityScreen
from database.data_manager import DataManager
from forms.parts_form import PartsForm



# Initialize the service container
services = ServiceContainer()    

def cleanup():
    """Ensures all database connections are closed on exit."""
    services.database_service.db_transaction_manager.close_all_connections() 

atexit.register(cleanup)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("800x600")
        self.main_container = Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.show_landing_page()

    def show_landing_page(self):
        self.clear_main_container()
        landing_frame = Frame(self.main_container)
        landing_frame.pack(expand=True)
        Button(landing_frame, text="Assemblies", command=self.show_assemblies).pack(pady=10)
        Button(landing_frame, text="Parts", command=self.show_parts).pack(pady=10)
        Button(landing_frame, text="Suppliers", command=self.show_suppliers).pack(pady=10)
        Button(landing_frame, text="Drawings", command=self.show_drawings).pack(pady=10)
        Button(landing_frame, text="Images", command=self.show_images).pack(pady=10)
        Button(landing_frame, text="Exit", command=self.quit).pack(pady=20)

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_assemblies(self):
        """Loads the Assemblies module dynamically."""
        self.clear_main_container()
        AssembliesScreen(self.main_container, self.show_landing_page)

    def show_parts(self):
        """Loads the Parts module dynamically."""
        self.clear_main_container()
        db_path = "path/to/your/database.db"  # Adjust the path to your database
        data_manager = DataManager(db_path)
        parts_window = PartsForm(self.main_container, VIEW_DEFINITION["PartsForm"], data_manager)
        parts_window.pack(fill=tk.BOTH, expand=True)
        
    def show_suppliers(self):
        """Loads the Suppliers module dynamically."""
        self.clear_main_container()
        frame = Frame(self.main_container)
        frame.pack(expand=True)
        Button(frame, text="Back to Main", command=self.show_landing_page).pack()

    def show_drawings(self):
        """Loads the Drawings module dynamically."""
        self.clear_main_container()
        # Add your code to show drawings

    def show_images(self):
        """Loads the Images module dynamically."""
        self.clear_main_container()
        # Add your code to show images

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()