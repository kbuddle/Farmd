import sys
import os

# Ensure src/ is in Python’s path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import atexit
import tkinter as tk
from tkinter import Tk, Frame, Button, PhotoImage
from PIL import Image, ImageTk  


from core.service_container import ServiceContainer
from ui.assemblies_screen import AssembliesScreen
from config.config_data import DEBUG, VIEW_DEFINITIONS, IMAGE_FOLDER
from ui.entity_screen import EntityScreen
from database.database_manager import DatabaseManager
from forms.entity_form import EntityForm
from src.landing_pages import LandingPage

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
        self.geometry("1200x800")
        
        # Set initial window size
        window_width = 1000
        window_height = 800

        # Center the window (using the method inside the class)
        self.center_window_vertically(window_width, window_height)

        self.main_container = Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.show_landing_page()

    def show_landing_page(self):
        """Loads the Landing Page into main container"""
        self.clear_main_container()  # Clear previous content
        self.lander = LandingPage(self.main_container, self)  # Create landing page inside main_container

    def clear_main_container(self):
        """Removes all widgets from the main container"""
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

    def center_window_vertically(window, width, height):
        """
        Centers a window vertically on the screen.
        
        Args:
            window (tk.Toplevel or tk.Tk): The window to center.
            width (int): The width of the window.
            height (int): The height of the window.
        """
        # Get the screen height
        screen_height = window.winfo_screenheight()
    
        # Calculate the x and y position
        x_position = (window.winfo_screenwidth() - width) // 2  # Horizontally centered
        y_position = (screen_height - height) // 2  # Vertically centered

        # Set the window size and position
        window.geometry(f"{width}x{height}+{x_position}+{y_position}")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()