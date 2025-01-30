import os
import tkinter as tk
from forms.select_entity import select_image_window

def image_selected_callback(image_path):
    print(f"Selected image: {image_path}")
    root.quit()  # ✅ Stop Tkinter after selection

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window

    image_folder = r"D:\FarmbotPythonV2\tests\MockData\images"

    if not os.path.exists(image_folder):
        print("Error: Image folder not found.")
    else:
        select_image_window(root, image_folder, image_selected_callback)

    root.mainloop()  # Keeps the window open, but will quit() when an image is selected

