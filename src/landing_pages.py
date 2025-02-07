import tkinter as tk
from tkinter import Frame, Label, Button
from PIL import Image, ImageTk
import os
from config.config_data import IMAGE_FOLDER

class LandingPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        
        self.pack(fill=tk.BOTH, expand=True)  # Use pack to match parent container
        
        self.background_image = None  # Store image reference
        
        self.create_landing_page()
        
        self.parent.after(100, self.resize_image)
        
    def create_landing_page(self):
        """Creates a structured landing page with three panels"""

        # TOP PANEL: Title and Subtitle
        top_panel = Frame(self, width=700, height=200, bg="lightblue")
        top_panel.pack(fill=tk.X, side=tk.TOP)

        title_label = Label(top_panel, text="Farmbot Builder", font=("Arial", 32, "bold"), bg="lightblue")
        title_label.pack(pady=(30, 5))

        subtitle_label = Label(top_panel, text="by Buddski 2025", font=("Arial", 16), bg="lightblue")
        subtitle_label.pack(pady=(0, 10))

        # MIDDLE PANEL: Canvas for Image
        self.mid_panel = Frame(self, bg="white")
        self.mid_panel.pack(fill=tk.BOTH, expand=True)

        # Lock initial height for canvas to avoid "Canvas too small"
        self.canvas = tk.Canvas(self.mid_panel, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # CALL FUNCTION TO LOAD IMAGE
        self.load_background_image()

        # BOTTOM PANEL: Buttons (with minimum height constraint)
        bottom_panel = Frame(self, bg="gray", height=100)
        bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_panel.pack_propagate(False)  # Prevents shrinking

        # Define button layout
        buttons = [
            ("Assemblies", self.controller.show_assemblies),
            ("Parts", self.controller.show_parts),
            ("Suppliers", self.controller.show_suppliers),
            ("Drawings", self.controller.show_drawings),
            ("Images", self.controller.show_images),
            #("Settings", self.controller.show_settings),
            #("Help", self.show_help),
            ("Exit", self.parent.quit)
        ]

        # Create buttons dynamically in rows
        for i, (text, command) in enumerate(buttons):
            btn = Button(bottom_panel, text=text, command=command, font=("Arial", 12), width=12, height=2)
            btn.grid(row=i // 4, column=i % 4, padx=5, pady=5)  # 4 columns layout

        # Make the button grid responsive
        for i in range(3):  # Rows
            bottom_panel.grid_rowconfigure(i, weight=1)
        for j in range(4):  # Columns
            bottom_panel.grid_columnconfigure(j, weight=1)

    def load_background_image(self):
        """Loads and resizes the background image into the canvas"""
        background_image_path = os.path.join(IMAGE_FOLDER, "farmbot_genesis_xl_v1.7.png")

        print(f"Here is the image file to be loaded: {background_image_path}")

        if not os.path.exists(background_image_path):
            print(f"Error: Image file not found at {background_image_path}")
            return  # Stop execution if the file does not exist

        try:
            img = Image.open(background_image_path)
            self.original_image = img  # Store original image reference

            # Resize and set the image
            self.resize_image()

            # Bind window resize event correctly
            self.parent.bind("<Configure>", self.resize_image)

        except Exception as e:
            print(f"Error loading image: {e}")

    def resize_image(self, event=None):
        """Resizes the image while maintaining aspect ratio"""
        if not hasattr(self, "original_image"):
            print("Error: No original image loaded")
            return

        # Ensure Canvas matches mid_panel size
        self.canvas.config(width=self.mid_panel.winfo_width(), height=self.mid_panel.winfo_height())

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10 or canvas_height < 10:
            print("Canvas too small to display image")
            return  # Avoid resizing if the canvas is too small

        print(f"Resizing image to fit within: {canvas_width}x{canvas_height}")

        # Maintain aspect ratio
        img_copy = self.original_image.copy()
        img_width, img_height = img_copy.size

        # Calculate the new size while maintaining aspect ratio
        scale_factor = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        img_resized = img_copy.resize((new_width, new_height), Image.LANCZOS)
        self.background_image = ImageTk.PhotoImage(img_resized)  # Store reference

        self.canvas.delete("all")  # Clear old images
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,  # Center the image
            image=self.background_image, anchor="center"
        )
        self.canvas.update()  # Force update


    # Placeholder functions
    def show_assemblies(self): print("Assemblies clicked")
    def show_parts(self): print("Parts clicked")
    def show_suppliers(self): print("Suppliers clicked")
    def show_drawings(self): print("Drawings clicked")
    def show_images(self): print("Images clicked")
    def show_settings(self): print("Settings clicked")
    def show_help(self): print("Help clicked")

if __name__ == "__main__":
    app = LandingPage()
    app.mainloop()
