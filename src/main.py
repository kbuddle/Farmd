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
        self.geometry("1000x800")
        self.main_container = Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.show_landing_page()

    from PIL import Image, ImageTk

    def show_landing_page(self):
        self.clear_main_container()

        # Create a Canvas widget to hold the background image (create only once)
        if not hasattr(self, "canvas"):
            self.canvas = tk.Canvas(self.main_container)
            self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create the button frame that will sit over the image (horizontally aligned at the top)
        button_frame = Frame(self.main_container, bg="white")  # Transparent background (same as canvas color)
        button_frame.pack(fill=tk.X, side=tk.TOP)  # Pack the frame horizontally at the top

        # Add buttons to the frame
        Button(button_frame, text="Assemblies", command=self.show_assemblies).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="Parts", command=self.show_parts).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="Suppliers", command=self.show_suppliers).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="Drawings", command=self.show_drawings).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="Images", command=self.show_images).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="Exit", command=self.quit).pack(side=tk.LEFT, padx=10)

        # Load and resize the background image
        background_image_path = os.path.join(IMAGE_FOLDER, "farmbot_genesis_xl_v1.7.png")
        print(f"here is image path: {background_image_path}")

        try:
            img = Image.open(background_image_path)
            # Convert the image to a format tkinter can work with
            self.background_image = ImageTk.PhotoImage(img)  # Keep the reference in an instance variable
            
            # If canvas already has an image, update it instead of recreating
            if hasattr(self, "canvas_image"):
                self.canvas.itemconfig(self.canvas_image, image=self.background_image)  # Update the image
            else:
                self.canvas_image = self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
            
            # Resize the image to fit the window initially
            self.resize_image(img)

            # Bind window resize event to update image size
            self.bind("<Configure>", lambda event: self.resize_image(img))
            
        except Exception as e:
            print(f"Error loading image: {e}")

    def resize_image(self, img):
        """Resizes the background image and updates it on the canvas"""
        new_width = self.winfo_width()
        new_height = self.winfo_height()

        # Resize the image to fit the window, maintaining the aspect ratio
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        # Update the image on the canvas
        self.background_image = ImageTk.PhotoImage(img_resized)  # Update reference
        self.canvas.itemconfig(self.canvas_image, image=self.background_image)  # Update image


            
    def resize_image(self, canvas, img):
        """Resizes the background image and updates it on the canvas"""
        new_width = self.winfo_width()
        new_height = self.winfo_height()

        # Resize the image to fit the window, maintaining the aspect ratio
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        # Update the image on the canvas
        self.background_image = ImageTk.PhotoImage(img_resized)  # Update reference
        canvas.itemconfig(self.canvas_image, image=self.background_image)  # Update image






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