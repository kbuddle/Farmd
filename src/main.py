import sys
import os

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button


from src.core.service_container import ServiceContainer
from src.ui.assemblies_screen import AssembliesScreen
from config.config_data import DEBUG, VIEW_DEFINITION
from src.ui.entity_screen import EntityScreen
from src.database.database_manager import DatabaseManager
from src.forms.parts_form import PartsForm
from src.forms.entity_form import EntityForm


# Initialize the service container
services = ServiceContainer()    

def cleanup():
    """Ensures all database connections are closed on exit."""
    db_manager = DatabaseManager()
    db_manager.close()  # ✅ Ensures proper connection closure

atexit.register(cleanup)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Home Screen")
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
        from src.database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        data_manager = db_service.fetch_all("Parts")
        parts_window = EntityForm(self.main_container, "Parts", VIEW_DEFINITION["PartsForm"], db_service, self)
        parts_window.pack(fill=tk.BOTH, expand=True)
        
    def show_suppliers(self):
        """Loads the Suppliers module dynamically."""
        from src.database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        data_manager = db_service.fetch_all("Suppliers")
        suppliers_window = EntityForm(self.main_container, "Suppliers", VIEW_DEFINITION["SuppliersForm"], db_service, self)
        suppliers_window.pack(fill=tk.BOTH, expand=True)

    def show_drawings(self):
        """Loads the Parts module dynamically."""
        from src.database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        data_manager = db_service.fetch_all("Drawings")
        drawings_window = EntityForm(self.main_container, "Drawings", VIEW_DEFINITION["DrawingsForm"], db_service, self)
        drawings_window.pack(fill=tk.BOTH, expand=True)

    def show_images(self):
        """Loads the Images module dynamically."""
        from src.database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        data_manager = db_service.fetch_all("Images")
        images_window = EntityForm(self.main_container, "Images", VIEW_DEFINITION["ImagesForm"], db_service, self)
        images_window.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()