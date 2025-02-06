import os
import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox, Label, Image, Button, Toplevel
from PIL import Image, ImageTk
from ui.ui_components import ScrollableFrame
from database.database_manager import DatabaseManager
from database.database_service import DatabaseService
from services.validation_service import ValidationService
from database.query_generator import QueryGenerator
from config.config_data import COLUMN_DEFINITIONS, IMAGE_FOLDER, ENTITY_ID_MAPPING
from ui.build_assembly_window import BuildAssemblyWindow 

import logging
logging.basicConfig(level=logging.DEBUG)

class EntityForm(tk.Frame):
    def __init__(self, parent, entity_name, tree_view_def, detail_view_def, data_manager, main_app):
        """
        Generic form for managing database entities like Parts, Drawings, etc.

        :param parent: Tkinter parent frame
        :param entity_name: Table name (e.g., "Parts", "Drawings")
        :param view_definition: Dictionary defining UI layout and fields
        :param data_manager: Database service instance
        """
        super().__init__(parent)
        self.entity_name = entity_name
        self.tree_view_def = tree_view_def
        self.detail_view_def = detail_view_def
        self.data_manager = data_manager
        self.main_app = main_app
        self.db_service= DatabaseService()  
        self.validation_service = ValidationService(COLUMN_DEFINITIONS, self.db_service) 
        
        self.item_data={}
        
        self.create_widgets()
        self.populate_tree()
        self.populate_detail_frame()

    def open_image_picker(self):
        """Opens a gallery view to pick an image and update AssemImageID."""
        
        # ✅ Step 1: Confirm with the user
        if not messagebox.askyesno("Select New Image", "Do you want to search for a new image?"):
            return

        # ✅ Step 2: Fetch images
        query = "SELECT ImageID, ImageFilename FROM Images"
        images = self.db_service.fetch_raw(query)  # ✅ Using fetch_raw()

        print(f"✅ Retrieved images: {images}")  # ✅ Debugging output to verify correct data format

        if not images:
            messagebox.showerror("Error", "No images found in the database.")
            return

        # ✅ Step 3: Create the image selection window
        popup = Toplevel(self)
        popup.title("Select an Image")
        popup.geometry("600x400")

        row, col, max_columns = 0, 0, 4
        for image_id, filename in images:
            image_path = os.path.join(IMAGE_FOLDER, filename)  # ✅ Uses correctly imported IMAGE_FOLDER
            if not os.path.exists(image_path):
                print(f"⚠️ Skipping missing image: {image_path}")
                continue  # Skip missing images

            img = Image.open(image_path)
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)

            # ✅ Create a frame for each image and label
            image_frame = ttk.Frame(popup)
            image_frame.grid(row=row, column=col, padx=5, pady=5)

            # ✅ Create the button with the image
            btn = Button(image_frame, image=img, command=lambda id=image_id: self.set_selected_image(id, popup))
            btn.image = img  # ✅ Keep reference to prevent garbage collection
            btn.pack()

            # ✅ Add a label below the image with filename
            lbl = Label(image_frame, text=filename, font=("Arial", 10))
            lbl.pack()

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    def set_selected_image(self, image_id, popup):
        """Displays a confirmation popup before saving the selected image."""

        # ✅ Open a confirmation popup
        confirm_popup = tk.Toplevel(self)
        confirm_popup.title("Confirm Image Selection")
        confirm_popup.geometry("300x150")

        # ✅ Label with confirmation message
        label = ttk.Label(confirm_popup, text="Do you want to save this image selection?")
        label.pack(pady=10)

        # ✅ Button Frame
        button_frame = ttk.Frame(confirm_popup)
        button_frame.pack(pady=10)

        # ✅ Save Image function (executes query)
        def save_image():
            self.execute_image_update(image_id)  # ✅ Calls the actual save function
            confirm_popup.destroy()
            popup.destroy()  # ✅ Closes both popups

        # ✅ Cancel function (closes popup without saving)
        def cancel():
            confirm_popup.destroy()  # ✅ Only closes the confirmation popup

        # ✅ Green "Save" Button (FULL background color)
        save_button = tk.Button(button_frame, text="Save", command=save_image,
                                font=("Arial", 10, "bold"), bg="green", fg="white", activebackground="darkgreen")
        save_button.pack(side=tk.LEFT, padx=10)

        # ✅ Red "Cancel" Button (FULL background color)
        cancel_button = tk.Button(button_frame, text="Cancel", command=cancel,
                                font=("Arial", 10, "bold"), bg="red", fg="white", activebackground="darkred")
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def execute_image_update(self, image_id):
        """Saves the selected image in the database and refreshes the displayed image."""

        # ✅ Determine table and ID column dynamically
        if self.entity_name == "Assemblies":
            id_column = "AssemblyID"
            table_name = "Assemblies"
        elif self.entity_name == "Parts":
            id_column = "PartID"
            table_name = "Parts"
        else:
            messagebox.showerror("Error", f"Unsupported entity: {self.entity_name}")
            return

        if id_column not in self.item_data or not self.item_data[id_column]:
            messagebox.showerror("Error", f"No {self.entity_name} selected.")
            return

        entity_id = self.item_data[id_column]  # ✅ Get the selected ID

        query = f"UPDATE {table_name} SET ImageID = ? WHERE {id_column} = ?"

        try:
            self.db_service.db_manager.execute_query(query, (image_id, entity_id))  # ✅ Update correct table
            print(f"✅ Image ID {image_id} set for {self.entity_name} {entity_id}.")
        except Exception as e:
            print(f"❌ Database update failed: {e}")
            return

        # ✅ Update `self.item_data` with the new ImageID
        self.item_data["ImageID"] = image_id

        # ✅ Reload the image in the UI
        self.load_detail_image()

    def open_build_window(self):
        """Opens the Build Assembly window for the selected assembly."""
        selected_item = self.entity_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No assembly selected to build.")
            return

        assembly_id = self.entity_tree.item(selected_item[0], "values")[0]
        assembly_name = self.entity_tree.item(selected_item[0], "values")[1]

        # ✅ Pass db_service when creating BuildAssemblyWindow
        BuildAssemblyWindow(self, int(assembly_id), assembly_name, self.db_service)
        
    def create_widgets(self):
        """Sets up the UI components including Treeview, Detail Frame, and Buttons."""
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Treeview frame expands
        self.grid_rowconfigure(1, weight=1)  # Detail frame expands
        self.grid_rowconfigure(2, weight=0)  # Button frame remains fixed

        # ✅ TOP SECTION: Treeview with Scrollbars
        self.tree_frame_container = ttk.Frame(self)
        self.tree_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # ✅ Ensure Treeview columns are properly defined
        self.entity_tree = ttk.Treeview(
            self.tree_frame_container,
            columns=list(self.tree_view_def["tree"]["columns"]),
            show="headings"  # ✅ Ensure column headings are visible
        )

        # ✅ Attach Scrollbars
        tree_scroll_y = ttk.Scrollbar(self.tree_frame_container, orient="vertical", command=self.entity_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.tree_frame_container, orient="horizontal", command=self.entity_tree.xview)

        self.entity_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # ✅ Grid positioning
        self.entity_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree_frame_container.grid_columnconfigure(0, weight=1)
        self.tree_frame_container.grid_rowconfigure(0, weight=1)

        # ✅ Ensure column headings are set correctly
        for field, details in self.tree_view_def["tree"]["headings"].items():
            self.entity_tree.heading(field, text=details)  # ✅ Set column heading
            column_width = self.tree_view_def["tree"].get("column_widths", {}).get(field, 100)  # Default width = 100
            self.entity_tree.column(field, width=column_width, anchor="w")  # Align left for readability

        self.entity_tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # ✅ Ensure `show="headings"` is set
        self.entity_tree["show"] = "headings"

        # ✅ MIDDLE SECTION: Detail Frame
        self.detail_frame_container = ScrollableFrame(self, text=self.detail_view_def["detail_frame"]["text"])
        self.detail_frame_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 📷 IMAGE INTEGRATION: Add Image Label inside Detail Frame
        self.detail_frame_container.grid_columnconfigure(3, weight=1)  # Allow space for image

        self.image_label = Label(self.detail_frame_container, cursor="hand2", text="(No image)")
        self.image_label.grid(row=0, column=3, padx=10, pady=10, sticky="e")  # Align to RHS

        # ✅ Load and display the image
        self.load_detail_image()

        # ✅ Bind left-click event to open image picker
        self.image_label.bind("<Button-1>", lambda event: self.open_image_picker())

        # ✅ BOTTOM SECTION: Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # ✅ Define buttons dynamically
        self.buttons = {
            "Save Changes": ttk.Button(self.button_frame, text="Save Changes", command=self.save_item, state=tk.DISABLED),
            "Clone Item": ttk.Button(self.button_frame, text="Clone Item", command=self.clone_item, state=tk.DISABLED),
            "Delete Item": ttk.Button(self.button_frame, text="Delete Item", command=self.delete_item, state=tk.DISABLED),
            "Add Item": ttk.Button(self.button_frame, text="Add Item", command=self.add_item),
            "Back": ttk.Button(self.button_frame, text="Back", command=lambda: self.main_app.show_landing_page()),
            "Clear": ttk.Button(self.button_frame, text="Clear", command=self.reset_to_defaults),
            "Build": ttk.Button(self.button_frame, text="Build", command= self.open_build_window, state=tk.DISABLED),
        }

        # ✅ Pack buttons
        for button in self.buttons.values():
            button.pack(side=tk.LEFT, padx=5)

        # ✅ Call update once to set initial states
        self.update_button_states()

    def add_build_button(entity_form):
        """Adds a Build button to the entity form if an assembly is selected."""
        if "Build" not in entity_form.buttons:
            entity_form.buttons["Build"] = ttk.Button(
                entity_form.button_frame, text="Build",
                command= lambda: entity_form.open_build_window()
            )
            entity_form.buttons["Build"].pack(side="left", padx=5)
      
    def update_button_states(self, is_new=False):
        """Updates button states based on the selected item or new entry."""
        selected_item = self.entity_tree.selection()
        has_selection = bool(selected_item)

        # Enable Save button if adding a new item
        self.buttons["Save Changes"].config(state=tk.NORMAL if is_new or has_selection else tk.DISABLED)

        # Enable Clone, Delete only if an item is selected
        self.buttons["Clone Item"].config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.buttons["Delete Item"].config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # Enable Build button only if an assembly is selected
        if "Build" in self.buttons:
            entity_type = self.entity_name.lower()
            self.buttons["Build"].config(state=tk.NORMAL if has_selection and entity_type == "assemblies" else tk.DISABLED)

    def populate_tree(self):
        """Fetches and displays all parts dynamically using DatabaseService (P2)."""

        if not hasattr(self.data_manager, "fetch_all_dict"):
            raise TypeError("Expected DatabaseService instance, got incorrect object type.")

        tree_columns = self.tree_view_def.get("tree", {}).get("columns", [])
        if not tree_columns:
            raise ValueError(f"❌ Tree columns are missing in view definition for {self.entity_name}")

        # ✅ Properly formatted SQL query
        query = f"SELECT * FROM {self.entity_name};"
        entity_data = self.data_manager.fetch_all_dict(query)

        # ✅ Clear tree before inserting new data
        self.entity_tree.delete(*self.entity_tree.get_children())

        # ✅ Insert data into treeview
        for record in entity_data:
            values = tuple("" if record[col] is None else record[col] for col in tree_columns if col in record)
            self.entity_tree.insert("", "end", values=values)

    def on_treeview_select(self, event):
        """Handles row selection in the treeview and updates the detail frame, including the image."""

        selected_item = self.entity_tree.selection()
        if not selected_item:
            print("⚠️ No item selected.")
            self.update_button_states()  # ✅ Disable buttons when nothing is selected
            return

        # ✅ Extract `item_id` from the first column of the selected row
        selected_values = self.entity_tree.item(selected_item[0], "values")
        print(f"🔍 Selected Row Values: {selected_values}")  # ✅ Debugging output

        if not selected_values:
            print("⚠️ No values found in selection.")
            return

        try:
            item_id = int(selected_values[0])  # ✅ Ensure ID is an integer
        except ValueError:
            print(f"❌ Invalid item ID: {selected_values[0]}")
            return

        print(f"🔍 Selected Item ID: {item_id}")  # ✅ Debugging Output

        # ✅ Define table and primary key mapping dynamically
        entity_table_mapping = {
            "Assemblies": "Assemblies",
            "Parts": "Parts",
            "Drawings": "Drawings",
            "Images": "Images",
            "Suppliers": "Suppliers"
        }

        entity_id_mapping = ENTITY_ID_MAPPING


        if self.entity_name not in entity_table_mapping:
            print(f"❌ Unsupported entity: {self.entity_name}")
            self.update_button_states()
            return

        # ✅ Assign dynamic table and ID column
        table_name = entity_table_mapping[self.entity_name]
        id_column = entity_id_mapping[self.entity_name]

        query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
        print(f"🔍 Running Query: {query} with item_id={item_id}")  # ✅ Debugging Output

        result = self.db_service.fetch_one_dict(query, (item_id,))

        if result:
            self.item_data = dict(result)  # ✅ Convert sqlite3.Row to dictionary
            print(f"✅ Selected {self.entity_name} Data: {self.item_data}")

            # ✅ Ensure ImageID is correctly used if applicable
            if "ImageID" in self.item_data and not self.item_data["ImageID"]:
                self.item_data["ImageID"] = 26  # ✅ Default to 26 (default.png)
                print(f"⚠️ No ImageID found, using default.")

            # ✅ Populate detail fields (pass item_data)
            self.populate_detail_frame(self.item_data)

            # ✅ Load image if ImageID is available
            if "ImageID" in self.item_data:
                self.load_detail_image()

            # ✅ Enable buttons after selection
            self.update_button_states()
        else:
            print(f"⚠️ No data found for {id_column}: {item_id}")
            self.update_button_states()

    def populate_detail_frame(self, prefill_data=None):
        """Populates the detail frame. If no data is provided, it clears fields."""
        
        print(f"🔹 Received Prefill Data: {prefill_data}")  # ✅ Debugging output

        # ✅ Clear previous fields & reset structure
        for widget in self.detail_frame_container.scrollable_frame.winfo_children():
            widget.destroy()

        self.fields = {}  # ✅ Ensure dictionary is reset
        row_index = 0  

        entry_style = ttk.Style()
        entry_style.configure("Readonly.TEntry", foreground="black", background="lightgray")  # ✅ Styling for readonly fields

        # ✅ If no prefill data, use an empty dictionary
        if not prefill_data:
            print("❌ No prefill data received. Defaulting all fields to empty.")
            prefill_data = {}

        print(f"🔍 Prefill Data Keys: {list(prefill_data.keys())}")  # ✅ Debugging output

        for field, details in self.detail_view_def["fields"].items():
            label_text = details["label"] + ":"
            
            # ✅ Create label
            label = ttk.Label(self.detail_frame_container.scrollable_frame, text=label_text)
            label.grid(row=row_index, column=0, padx=5, pady=2, sticky="w")

            # ✅ Create entry field
            entry = ttk.Entry(self.detail_frame_container.scrollable_frame, width=details["width"])

            # ✅ Retrieve value from prefill_data
            value = prefill_data.get(field, "")
            value = "" if value is None else value  # ✅ Ensure None is displayed as ""
            print(f"🔹 Setting {field} to '{value}'")  # ✅ Debugging output

            entry.insert(0, str(value))  # ✅ Insert value as string

            # ✅ Apply readonly styling if necessary
            if not details.get("edit", True):
                entry.configure(state="readonly", style="Readonly.TEntry")

            entry.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            
            entry.bind("<KeyRelease>", lambda event: self.enable_save_button())
            
            self.fields[field] = entry  # ✅ Store reference to entry field

            row_index += 1  

        # ✅ Force UI refresh to prevent stale data issues
        self.detail_frame_container.scrollable_frame.update_idletasks()  
        self.update_button_states()  # ✅ Ensure buttons are enabled/disabled properly

        print("✅ Detail Frame Successfully Updated.")  # ✅ Debugging output

    def load_entity_details(self, event):
        """Loads selected row details into the form fields when a Treeview row is clicked."""
        
        print("🔹 Entered `load_entity_details()`")  # ✅ Debugging output

        selected_item = self.entity_tree.selection()
        if not selected_item:
            print("❌ No item selected in Treeview.")
            return  

        selected_values = self.entity_tree.item(selected_item, "values")
        print(f"🔍 Selected Treeview Item: {selected_values}")  # ✅ Debugging output

        if not selected_values:
            print("❌ No values found in selected Treeview item.")
            return  

        # ✅ Debugging: Check if `self.data_manager` exists and has `get_primary_key()`
        if not hasattr(self.data_manager, "get_primary_key"):
            print("❌ ERROR: `self.data_manager` does not have `get_primary_key()`!")
            return

        print("🔍 Calling `get_primary_key()`...")  # ✅ Debugging output

        primary_key_column = self.data_manager.get_primary_key(self.entity_name)

        if not primary_key_column:
            print(f"❌ Primary key not found for {self.entity_name}. Check column definitions.")
            return

        print(f"✅ Retrieved Primary Key: {primary_key_column}")  # ✅ Debugging output

        reference_value = selected_values[0]  # ✅ First column value should be the ID

        print(f"🔍 Looking for record where {primary_key_column} = {reference_value}")  # ✅ Debugging output

        # ✅ Fetch all records for this entity
        full_records = self.data_manager._dict(self.entity_name)

        print(f"🔍 Full Records Retrieved: {full_records}")  # ✅ Debugging output

        # ✅ Ensure keys in `full_records` match the Treeview selection keys
        matching_record = None
        for record in full_records:
            print(f"🛠️ Checking record: {record}")  # ✅ Debugging output
            if str(record.get(primary_key_column, "")) == str(reference_value):
                matching_record = record
                break  # ✅ Stop looping once a match is found

        if not matching_record:
            print(f"❌ No matching record found for {primary_key_column}={reference_value}")
            return  

        print(f"✅ Found record: {matching_record}")  # ✅ Debugging output

        # ✅ Populate the detail frame with fetched data
        self.populate_detail_frame(prefill_data=matching_record)
   
    def save_item(self):
        """Saves a new entity record or updates an existing one while ensuring correct validation rules."""
        selected_item = self.entity_tree.selection()
        is_new_entry = not selected_item  # Determines new vs update

        # ✅ Fetch cleaned data (already validated)
        form_data = self.get_form_data(is_new_entry, self.db_service)    
        if not form_data:
            print("❌ No data provided for saving.")
            return

        print(f"Check state of new_entry {is_new_entry}, form_data {form_data}, and self.entity_name {self.entity_name} 3 args to validate form data")

        try:
            # ✅ Pass correct form_data instead of `selected_item`
            validated_data = self.validation_service.validate_form_data(self.entity_name, form_data, is_new_entry)

            if is_new_entry:
                new_item_id = self.db_service.add_item(self.entity_name, validated_data)
                print(f"✅ New {self.entity_name} record added with ID {new_item_id}.")
            else:
                primary_key_column = self.db_service.get_primary_key(self.entity_name)
                reference_value = self.entity_tree.item(selected_item[0], "values")[0]
                validated_data[primary_key_column] = reference_value  # Ensure PK exists for update

                self.db_service.update_item(self.entity_name, validated_data)
                print(f"✅ {self.entity_name} record updated.")

        except Exception as e:
            print(f"❌ Validation/Database Error in save item: {e}")

        self.refresh_tree()
        self.clear_form()  # Reset form after saving

    def edit_item(self):
        """ Edits the selected entity record. """
        selected_item = self.entity_tree.selection()
        if not selected_item:
            print("❌ No item selected for editing.")
            return

        item_id = self.entity_tree.set(selected_item, "ID")  # Assumes "ID" is the primary key
        form_data = self.get_form_data()
        if not form_data:
            print("❌ No changes detected.")
            return

        self.data_manager.edit(self.entity_name, item_id, form_data)
        self.refresh_tree()
        print(f"✅ Item {item_id} updated successfully.")

    def add_item(self):
        """Prepares the detail frame for adding a new item."""

        # ✅ Clear selection to ensure a new record is being created
        self.entity_tree.selection_remove(self.entity_tree.selection())

        # ✅ Reset item_data for new record
        self.item_data = {}
        self.clear_form()

        # ✅ Handle special cases (Drawings require a valid `DrawingPath`)
        if self.entity_name == "Drawings":
            self.item_data["DrawingPath"] = "default_path.pdf"  # ✅ Ensures NOT NULL constraint is met

        # ✅ Populate detail frame with new blank entry (or defaults)
        self.populate_detail_frame(self.item_data)

        # ✅ Enable Save button for new entries
        self.update_button_states(is_new=True)

        print(f"✅ Ready to add a new {self.entity_name}. Enter details and save.")

    def clone_item(self):
        """Clones the selected item and loads it into the detail frame for editing."""

        selected_item = self.entity_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No item selected for cloning.")
            return

        # ✅ Extract and validate `item_id`
        item_id = self.entity_tree.item(selected_item[0], "values")[0]  # ✅ Get ID from first column
        try:
            item_id = int(item_id)  # ✅ Ensure it's an integer
        except ValueError:
            print(f"❌ Invalid item ID: {item_id}")
            return

        # ✅ Dynamically determine table and primary key column
        entity_id_mapping = {
            "Assemblies": "AssemblyID",
            "Parts": "PartID",
            "Drawings": "DrawingID",
            "Images": "ImageID",
            "Suppliers": "SupplierID"
        }

        if self.entity_name not in entity_id_mapping:
            print(f"❌ Unsupported entity: {self.entity_name}")
            return

        id_column = entity_id_mapping[self.entity_name]
        table_name = self.entity_name

        # ✅ Fetch the record to clone
        query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
        result = self.db_service.fetch_one_dict(query, (item_id,))

        if result:
            self.cloned_data = dict(result)  # ✅ Convert sqlite3.Row to dictionary
            print(f"✅ Cloned Data Before Modifications: {self.cloned_data}")

            # ✅ Remove the original ID to allow auto-increment
            if id_column in self.cloned_data:
                del self.cloned_data[id_column]  # ✅ Remove ID for auto-increment

            # ✅ Ensure `ParentAssemblyID` is handled correctly (NULL if needed)
            if "ParentAssemblyID" in self.cloned_data and not self.cloned_data["ParentAssemblyID"]:
                self.cloned_data["ParentAssemblyID"] = None  # ✅ Handles empty string cases too

            # ✅ Load cloned data into the detail frame for editing
            self.populate_detail_frame(self.cloned_data)

            # ✅ Clear Treeview selection to prevent mistaken updates
            self.entity_tree.selection_remove(self.entity_tree.selection())

            # ✅ Inform user to make changes before saving
            messagebox.showinfo("Success", "Cloned item loaded for editing. Make changes and save.")

            print(f"✅ Cloned Data Ready for Editing: {self.cloned_data}")
        else:
            print(f"⚠️ No data found for {id_column}: {item_id}")

    def delete_item(self):
        """Deletes the selected item after confirmation and handles errors properly."""
        selected_item = self.entity_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Warning", "No item selected for deletion.")
            return

        # ✅ Retrieve item ID safely
        item_values = self.entity_tree.item(selected_item[0], "values")
        if not item_values or len(item_values) == 0:
            print("❌ Unable to retrieve item ID for deletion.")
            return
        item_id = item_values[0]

        # ✅ Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
        if not confirm:
            return

        # ✅ Fetch primary key dynamically
        id_column = self.db_service.get_primary_key(self.entity_name)
        if not id_column:
            print(f"❌ Unable to determine primary key for {self.entity_name}")
            return

        table_name = self.entity_name
        query = f"DELETE FROM {table_name} WHERE {id_column} = ?"

        try:
            print(f"🗑 Attempting to delete {self.entity_name} | ID: {item_id} | Column: {id_column}")
            self.data_manager.execute_query(query, (item_id,))
            print(f"✅ Successfully deleted {self.entity_name} ID: {item_id}")
        except sqlite3.IntegrityError:
            print(f"❌ Cannot delete {self.entity_name} ID {item_id} due to foreign key constraints.")
            messagebox.showerror("Error", f"Cannot delete {self.entity_name}. It is referenced in other records.")
        except Exception as e:
            print(f"❌ Delete Error: {e}")
            messagebox.showerror("Error", f"Failed to delete {self.entity_name}: {e}")

        # ✅ Refresh treeview after deletion
        self.refresh_tree()
        self.reset_to_defaults()

    def clear_form(self):
        """ Clears all fields in the form after adding an item. """
        for field in self.fields.values():
            field.delete(0, tk.END)

    def get_form_data(self, is_new_entry, db_service):
        """ ✅ Passes data directly to ValidationService (no extra processing) """
        raw_form_data = {
            field: (widget.get().strip() if widget.get().strip().lower() != "none" else None)
            for field, widget in self.fields.items()
        }
        print(f"here is {raw_form_data}")
        print(f" is new entry state with get form data is {is_new_entry}")
        try:
            # ✅ Use ValidationService to process and clean data
            cleaned_data = self.validation_service.extract_form_data(raw_form_data, self.entity_name, is_new_entry)
            print(f"Here is cleaned data {cleaned_data}")
            return cleaned_data
        except Exception as e:
            print(f"❌ Error processing form data: {e}")
            return None  # Return None to prevent invalid data from being saved

    def refresh_tree(self):
        """ Refreshes the treeview after an update. """
        self.entity_tree.delete(*self.entity_tree.get_children())  # Clear treeview
        self.populate_tree()  # Reload data
   
    def load_detail_image(self):
        """ 📷 Loads and displays the correct image based on ImageID. """
        
        self.primary_key_column = ENTITY_ID_MAPPING.get(self.entity_name)  # ✅ Get primary key column name
        if not self.primary_key_column:
            raise ValueError(f"❌ No primary key mapping found for entity: {self.entity_name}")

        # ✅ Ensure self.item_data contains the primary key before using it
        if self.primary_key_column not in self.item_data:
            print(f"❌ Missing {self.primary_key_column} in item_data: {self.item_data}")
            return  # Stop execution to prevent KeyError

        entity_id = self.item_data[self.primary_key_column]  # ✅ Now it's safe to access

        # ✅ Fetch the latest ImageID from the database
        query = f"SELECT ImageID FROM {self.entity_name} WHERE {self.primary_key_column} = ?"
        result = self.db_service.fetch_one_dict(query, (entity_id,))

        if result and "ImageID" in result:
            self.item_data["ImageID"] = result["ImageID"]

        image_id = int(self.item_data.get("ImageID", 26))  # ✅ Ensure it's an integer
        print(f"🔍 Fetching image for ImageID: {image_id}")

        # ✅ Query the latest image filename from the database
        query = "SELECT ImageFileName FROM Images WHERE ImageID = ?"
        result = self.db_service.fetch_one_dict(query, (image_id,))
        print(f"🔍 Database Fetch Result: {result}")

        # ✅ Safely retrieve image filename (fallback to default.png)
        image_filename = result.get("ImageFileName", "default.png") if result else "default.png"
        print(f"✅ Selected Image FileName: {image_filename}")

        image_path = os.path.join(IMAGE_FOLDER, image_filename)
        print(f"🔍 Checking for image: {image_path}")

        # ✅ Ensure the file exists, otherwise use `default.png`
        if not os.path.exists(image_path):
            print(f"⚠️ Image not found: {image_path}, using default.png")
            image_path = os.path.join(IMAGE_FOLDER, "default.png")

        # ✅ Try to load the image, falling back to default if it fails
        try:
            img = Image.open(image_path)
            img = img.resize((400, 300), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"❌ Error loading image {image_path}: {e}, using default.png")
            img = Image.open(os.path.join(IMAGE_FOLDER, "default.png"))
            img = img.resize((400, 300), Image.Resampling.LANCZOS)

        img = ImageTk.PhotoImage(img)

        print("✅ Image loaded successfully!")

        self.image_label.config(image=img)
        self.image_label.image = img  # ✅ Prevent garbage collection
        self.image_label.update_idletasks()  # ✅ Force UI refresh

    def clear_detail_form(self):
        """Clears all input fields, including primary and foreign keys, and deselects the treeview selection."""

        primary_key_field = self.db_service.get_primary_key(self.entity_name)  # ✅ Get PK column name

        for field, widget in self.fields.items():
            # ✅ Temporarily enable read-only fields to allow clearing
            if widget.cget("state") == "readonly":
                widget.configure(state="normal")

            widget.delete(0, "end")  # ✅ Clear input

            # ✅ Ensure PK is fully removed
            if field == primary_key_field:
                widget.insert(0, "")  # ✅ Ensure it's visually cleared

            # ✅ Restore read-only state if necessary
            if self.detail_view_def["fields"].get(field, {}).get("edit", True) is False:
                widget.configure(state="readonly")

        # ✅ Deselect any selected item in the treeview
        self.entity_tree.selection_remove(self.entity_tree.selection())

        print("✅ Detail form cleared, including primary & foreign keys.")

    def reset_to_defaults(self):
        """Resets the detail form to default values, including primary key and foreign keys."""

        # ✅ Get primary key field name
        primary_key_field = self.db_service.get_primary_key(self.entity_name)

        # ✅ Retrieve default values from the validation service
        default_data = {
            field: details.get("default", "")  # Use the default if defined, otherwise empty
            for field, details in self.detail_view_def["fields"].items()
        }

        for field, widget in self.fields.items():
            # ✅ Temporarily enable read-only fields to allow resetting
            if widget.cget("state") == "readonly":
                widget.configure(state="normal")

            # ✅ Reset the value to the default (or empty if no default exists)
            widget.delete(0, "end")
            widget.insert(0, str(default_data.get(field, "")))

            # ✅ Ensure PK is properly cleared
            if field == primary_key_field:
                widget.delete(0, "end")  # Fully remove ID if auto-incremented

            # ✅ Restore read-only state if necessary
            if self.detail_view_def["fields"].get(field, {}).get("edit", True) is False:
                widget.configure(state="readonly")

        # ✅ Deselect any selected item in the treeview
        self.entity_tree.selection_remove(self.entity_tree.selection())

        print("✅ Detail form reset to default values.")

    def enable_save_button(self):
        """Enables the Save button when user starts typing."""
        self.buttons["Save Changes"].config(state=tk.NORMAL)
   
    


        