import os
from tkinter import Toplevel, Frame, Label, Button, Entry, ttk
from PIL import Image, ImageTk

def select_entity_window(parent, entity_type, selection_callback):
    """
    Creates a reusable entity selection window.

    Args:
        parent (tk.Widget): The parent frame or window.
        entity_type (str): The type of entity being selected (e.g., 'Part', 'Assembly', 'Drawing', 'Supplier', 'Image').
        selection_callback (function): Function to call with selected entity data.

    Returns:
        None
    """
    config = entity_config.get(entity_type, {})

    if not config:
        print(f"Error: No configuration found for entity type '{entity_type}'")
        return

    window = Toplevel(parent)
    window.title(config.get("title", "Select Entity"))
    window.geometry("500x400")

    # Search Bar
    search_frame = Frame(window)
    search_frame.pack(fill="x", padx=10, pady=5)
    Label(search_frame, text="Search:").pack(side="left")
    search_entry = Entry(search_frame)
    search_entry.pack(side="left", expand=True, fill="x", padx=5)

    # Table or Thumbnails
    if config.get("thumbnail", False):
        frame = Frame(window)
        frame.pack(fill="both", expand=True)
        # Placeholder for image thumbnails
    else:
        # Treeview with dynamically retrieved column names & labels
        columns = config["columns"]
        tree = ttk.Treeview(window, columns=list(columns.keys()), show="headings")

        for col_key, col_data in columns.items():
            tree.heading(col_key, text=col_data["display_name"])
            tree.column(col_key, width=100)

        tree.pack(fill="both", expand=True)

    # Select Button
    def on_select():
        selected_item = tree.selection()
        if selected_item:
            item_data = tree.item(selected_item, "values")
            selection_callback(item_data)
            window.destroy()

    select_button = Button(window, text="Select", command=on_select)
    select_button.pack(pady=5)

    return window

def select_image_window(parent, image_folder, selection_callback):
    """
    Creates a window for selecting an image from thumbnails.

    Args:
        parent (tk.Widget): The parent window.
        image_folder (str): Folder path containing images.
        selection_callback (function): Callback function to return selected image path.

    Returns:
        None
    """
    window = Toplevel(parent)
    window.title("Select Image")
    window.geometry("800x800")

    # Container for thumbnails
    thumbnail_frame = Frame(window)
    thumbnail_frame.pack(fill="both", expand=True)

    # Load images
    images = [f for f in os.listdir(image_folder) if f.lower().endswith(("png", "jpg", "jpeg"))]

    if not images:
        Label(thumbnail_frame, text="No images found in folder.").pack()
        return

    # Function to select an image
    def on_select(image_name):
        selected_path = os.path.join(image_folder, image_name)
        selection_callback(selected_path)
        window.destroy()

    # Display images as buttons
    row, col = 0, 0
    for image_name in images:
        try:
            img_path = os.path.join(image_folder, image_name)
            img = Image.open(img_path)
            img.thumbnail((100, 100))  # Resize for thumbnails
            img = ImageTk.PhotoImage(img)

            # ✅ Create a frame to hold both the image and label
            item_frame = Frame(thumbnail_frame)
            item_frame.grid(row=row, column=col, padx=10, pady=10)

            # ✅ Add image button inside item_frame
            btn = Button(item_frame, image=img, command=lambda i=image_name: on_select(i))
            btn.image = img  # Keep reference to avoid garbage collection
            btn.pack(side="top")  # ✅ Image on top

            # ✅ Add filename label below the image inside item_frame
            lbl = Label(item_frame, text=image_name, font=("Arial", 10))
            lbl.pack(side="bottom")  # ✅ Label below image

            # ✅ Adjust grid position (5 images per row)
            col += 1
            if col > 4:
                col = 0
                row += 1

        except Exception as e:
            print(f"Error loading image {image_name}: {e}")

    return window
