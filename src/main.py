import sys
import os
import time

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

        # ✅ Load background image ONCE and keep reference
        background_image_path = os.path.join(IMAGE_FOLDER, "farmbot_genesis_xl_v1.7.png")
        try:
            self.original_image = Image.open(background_image_path)
            self.background_image = ImageTk.PhotoImage(self.original_image)  # ✅ Ensure it's always available
        except Exception as e:
            print(f"⚠️ Error loading initial background image: {e}")
            self.original_image = None
            self.background_image = None

        self.show_landing_page()

        # ✅ Force first-time resize after UI initializes
        self.after(500, self.resize_image)  # ✅ Small delay ensures UI is ready


    from PIL import Image, ImageTk

    def show_landing_page(self):
        """Displays the landing page and ensures the background image fits the window."""
        print("🔄 Loading Landing Page...")  # ✅ Debug print
        self.clear_main_container()

        # ✅ Create Canvas FIRST (Ensures image loads behind buttons)
        self.canvas = tk.Canvas(self.main_container)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)  # ✅ Ensures it stays in the background

        # ✅ Create Button Frame on top
        self.button_frame = Frame(self.main_container, bg="white")
        self.button_frame.place(x=0, y=0, relwidth=1, height=50)  # ✅ Ensures buttons stay visible

        buttons = {
            "Assemblies": self.show_assemblies,
            "Parts": self.show_parts,
            "Suppliers": self.show_suppliers,
            "Drawings": self.show_drawings,
            "Images": self.show_images,
            "Exit": self.quit,
        }

        for text, command in buttons.items():
            Button(self.button_frame, text=text, command=command).pack(side=tk.LEFT, padx=10)

        print("✅ Buttons created!")  # ✅ Debug print

        # ✅ Force Image Refresh
        self.load_image()
        self.refresh_image()

        # ✅ Rebind resize event (ensure old events are cleared)
        self.unbind("<Configure>")  
        self.after(300, lambda: self.bind("<Configure>", self.resize_image))



    def resize_image(self, event=None):
        """Resizes and updates the background image to fit the current window."""
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            print("⚠️ Resize aborted: Canvas no longer exists.")
            return

        new_width = self.winfo_width()
        new_height = self.winfo_height()

        if new_width < 50 or new_height < 50:
            return  # Prevent resizing if the window is too small

        try:
            # ✅ Ensure image is loaded
            if not hasattr(self, "original_image"):
                background_image_path = os.path.join(IMAGE_FOLDER, "farmbot_genesis_xl_v1.7.png")
                self.original_image = Image.open(background_image_path)

            # ✅ Resize the image based on the actual window size
            img_resized = self.original_image.resize((new_width, new_height), Image.LANCZOS)

            # ✅ Convert to a format Tkinter can display
            self.background_image = ImageTk.PhotoImage(img_resized)

            # ✅ Ensure the canvas image is properly recreated when returning to the landing page
            if hasattr(self, "canvas_image") and self.canvas_image:
                self.canvas.itemconfig(self.canvas_image, image=self.background_image)
            else:
                self.canvas_image = self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

            print(f"✅ Background image resized to {new_width}x{new_height}")

        except Exception as e:
            print(f"⚠️ Error updating background image: {e}")

            
    def refresh_image(self):
        """Ensures the background image exists before using it."""
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            print("⚠️ Canvas not found, skipping image update.")
            return  

        print("🔄 Refreshing image...")  # ✅ Debug print

        # ✅ Ensure background image is loaded before using it
        if self.background_image is None:
            print("⚠️ Background image missing, forcing reload...")
            self.load_image()  # Explicitly load the image if it's missing

        # ✅ Always recreate the canvas image
        self.canvas.delete("all")  # ✅ Clear the old image to prevent overlap
        self.canvas_image = self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        self.resize_image()  # ✅ Ensure the image fits the window


    def load_image(self):
        """Forces an image reload every time."""
        try:
            print("🔄 Loading new image...")  # ✅ Debug print
            background_image_path = os.path.join(IMAGE_FOLDER, "farmbot_genesis_xl_v1.7.png")

            # ✅ Force reloading the image from disk every time
            self.original_image = Image.open(background_image_path)
            self.background_image = ImageTk.PhotoImage(self.original_image)

            print("✅ Image successfully loaded!")
        except Exception as e:
            print(f"⚠️ Error loading background image: {e}")



    def clear_main_container(self):
        """Clears the main container and unbinds events to prevent errors."""
        self.unbind("<Configure>")  # ✅ Unbind to prevent callbacks after canvas is destroyed
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