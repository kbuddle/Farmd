import sys
import os

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button


from core.service_container import ServiceContainer
from ui.assemblies_screen import AssembliesScreen
from config.config_data import DEBUG, VIEW_DEFINITIONS
from ui.entity_screen import EntityScreen
from database.database_manager import DatabaseManager
from forms.entity_form import EntityForm

print("✅ main.py has started executing!")

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
        from database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH, VIEW_DEFINITIONS
        db_path = DATABASE_PATH
        
        db_service = DatabaseService(db_path)
        
        self.clear_main_container()
                     
        tree_view_def = VIEW_DEFINITIONS["AssembliesFormA2"]  # ✅ Treeview should use P2
        detail_view_def = VIEW_DEFINITIONS["AssembliesFormA1"]  # ✅ Detail frame should use P1

        assemblies_window = EntityForm(self.main_container, "Assemblies", tree_view_def, detail_view_def, db_service, self)
 
        assemblies_window.pack(fill=tk.BOTH, expand=True)

    def show_parts(self):
        """Loads the Parts module dynamically."""
        from database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH, VIEW_DEFINITIONS
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        
        tree_view_def = VIEW_DEFINITIONS["PartsFormP2"]  # ✅ Treeview should use P2
        detail_view_def = VIEW_DEFINITIONS["PartsFormP1"]  # ✅ Detail frame should use P1

        parts_window = EntityForm(self.main_container, "Parts", tree_view_def, detail_view_def, db_service, self)
        parts_window.pack(fill=tk.BOTH, expand=True)
        
    def show_suppliers(self):
        """Loads the Suppliers module dynamically."""
        from database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH, VIEW_DEFINITIONS
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
       
        tree_view_def = VIEW_DEFINITIONS["SuppliersFormS2"]  # ✅ Treeview should use P2
        detail_view_def = VIEW_DEFINITIONS["SuppliersFormS1"]  # ✅ Detail frame should use P1

        suppliers_window = EntityForm(self.main_container, "Suppliers", tree_view_def, detail_view_def, db_service, self)
        suppliers_window.pack(fill=tk.BOTH, expand=True)

    def show_drawings(self):
        """Loads the Parts module dynamically."""
        from database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH, VIEW_DEFINITIONS
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
        
        
        tree_view_def = VIEW_DEFINITIONS["DrawingsFormD2"]  # ✅ Treeview should use P2
        detail_view_def = VIEW_DEFINITIONS["DrawingsFormD1"]  # ✅ Detail frame should use P1

        drawings_window = EntityForm(self.main_container, "Drawings", tree_view_def, detail_view_def, db_service, self)

        drawings_window.pack(fill=tk.BOTH, expand=True)

    def show_images(self):
        """Loads the Images module dynamically."""
        from database.database_service import DatabaseService
        from config.config_data import DATABASE_PATH, VIEW_DEFINITIONS
        db_path = DATABASE_PATH
        db_service = DatabaseService(db_path)
        self.clear_main_container()
       

        tree_view_def = VIEW_DEFINITIONS["ImagesFormI2"]  # ✅ Treeview should use P2
        detail_view_def = VIEW_DEFINITIONS["ImagesFormI1"]  # ✅ Detail frame should use P1

        images_window = EntityForm(self.main_container, "Images", tree_view_def, detail_view_def, db_service, self)

        images_window.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()