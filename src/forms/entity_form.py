import os
import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox, Label, Image
from PIL import Image, ImageTk
from src.ui.ui_components import ScrollableFrame
from src.database.database_manager import DatabaseManager
from src.database.database_service import DatabaseService
from src.services.validation_service import ValidationService
from src.database.query_generator import QueryGenerator
from config.config_data import COLUMN_DEFINITIONS, IMAGE_FOLDER
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
        self.validation_service = ValidationService(COLUMN_DEFINITIONS) 
        
        self.item_data={}
        
        self.create_widgets()
        self.populate_tree()
        self.populate_detail_frame()

    def create_widgets(self):
        """Sets up the UI components including Treeview, Detail Frame, and Buttons."""
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Treeview frame expands
        self.grid_rowconfigure(1, weight=1)  # Detail frame expands
        self.grid_rowconfigure(2, weight=0)  # Button frame remains fixed

        # ✅ Top Section: Treeview with Scrollbar
        self.tree_frame_container = ttk.Frame(self)
        self.tree_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        self.entity_tree = ttk.Treeview(
            self.tree_frame_container,
            columns=list(self.tree_view_def["tree"]["columns"]),
            show="headings"
        )

        # Attach scrollbars
        tree_scroll_y = ttk.Scrollbar(self.tree_frame_container, orient="vertical", command=self.entity_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.tree_frame_container, orient="horizontal", command=self.entity_tree.xview)

        self.entity_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # Grid positioning
        self.entity_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree_frame_container.grid_columnconfigure(0, weight=1)
        self.tree_frame_container.grid_rowconfigure(0, weight=1)

        # ✅ Middle Section: Detail Frame (Uses P1)
        self.detail_frame_container = ScrollableFrame(self, text=self.detail_view_def["detail_frame"]["text"])
        self.detail_frame_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 📷 IMAGE INTEGRATION: Add Image Label inside Detail Frame (using grid)
        self.detail_frame_container.grid_columnconfigure(3, weight=1)  # Allow space for image

        self.image_label = Label(self.detail_frame_container)
        self.image_label.grid(row=0, column=3, padx=10, pady=10, sticky="e")  # Align to RHS

        # Load and display the image
        self.load_detail_image()

        # ✅ Bottom Section: Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # ✅ Define buttons dynamically
        self.buttons = {
            "Save Changes": ttk.Button(self.button_frame, text="Save Changes", command=self.save_item, state=tk.DISABLED),
            "Clone Item": ttk.Button(self.button_frame, text="Clone Item", command=self.clone_item, state=tk.DISABLED),
            "Delete Item": ttk.Button(self.button_frame, text="Delete Item", command=self.delete_item, state=tk.DISABLED),
            "Add Item": ttk.Button(self.button_frame, text="Add Item", command=self.add_item),
            "Back": ttk.Button(self.button_frame, text="Back", command=lambda: self.main_app.show_landing_page())
        }

        # ✅ Pack buttons
        for button in self.buttons.values():
            button.pack(side=tk.LEFT, padx=5)

        # ✅ Call update once to set initial states
        self.update_button_states()


    def update_button_states(self, event=None):
        """Updates button states based on selection in the Treeview."""
        selected_item = self.entity_tree.selection()

        if selected_item:
            # ✅ Enable edit-related buttons when an item is selected
            self.buttons["Save Changes"].config(state=tk.NORMAL)
            self.buttons["Clone Item"].config(state=tk.NORMAL)
            self.buttons["Delete Item"].config(state=tk.NORMAL)
            self.buttons["Add Item"].config(state=tk.DISABLED)
        else:
            # ✅ Enable add functionality when no item is selected
            self.buttons["Save Changes"].config(state=tk.DISABLED)
            self.buttons["Clone Item"].config(state=tk.DISABLED)
            self.buttons["Delete Item"].config(state=tk.DISABLED)
            self.buttons["Add Item"].config(state=tk.NORMAL)

    def populate_tree(self):
        """Fetches and displays all parts dynamically using DatabaseService (P2)."""

        if not hasattr(self.data_manager, "fetch_all"):
            raise TypeError("Expected DatabaseService instance, got incorrect object type.")
        
        tree_columns = self.tree_view_def.get("tree", {}).get("columns", [])  # ✅ Use P2 definition
        if not tree_columns:
            raise ValueError(f"❌ Tree columns are missing in view definition for {self.entity_name}")

        # ✅ Fetch all data using `fetch_all()`
        entity_data = self.data_manager.fetch_all(self.entity_name)

       # print(f"🔍 Treeview Fetch Data: {entity_data}")  # ✅ Debugging output

        # ✅ Clear tree before inserting new data
        self.entity_tree.delete(*self.entity_tree.get_children())

        # ✅ Insert data into treeview
        for record in entity_data:
            values = tuple(record[col] for col in tree_columns if col in record)
            #print(f"🌟 Inserting row: {values}")  # ✅ Debugging output
            self.entity_tree.insert("", "end", values=values)

    def on_treeview_select(self, event):
        """Handles Treeview selection event to populate detail frame."""
        print("Getting to here!!! treeview select")
        self.load_entity_details(event)
        self.update_button_states()

        selected_items = self.entity_tree.selection()
        if not selected_items:
            logging.debug("No item selected in Treeview.")
            return

        selected_item = selected_items[0]
        item_data = self.entity_tree.item(selected_item).get("values", [])

        if not item_data:
            logging.debug(f"Selected item {selected_item} has no values.")
            return

        column_names = self.tree_view_def.get("tree", {}).get("columns", [])
        if not column_names:
            logging.warning("Treeview column definitions are missing.")
            return

        prefill_data = dict(zip(column_names, item_data))
        logging.debug(f"Prefilled Data: {prefill_data}")

        self.populate_detail_frame(prefill_data)

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

        # ✅ Check if `prefill_data` is valid before proceeding
        if prefill_data is None:
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

            # ✅ Check if the key exists in prefill_data (avoid mismatches)
            if field in prefill_data:
                value = prefill_data[field]
            else:
                print(f"⚠️ Warning: {field} not found in prefill data. Using default empty string.")
                value = ""

            print(f"🔹 Setting {field} to '{value}'")  # ✅ Debugging output

            entry.insert(0, str(value))  # ✅ Insert value as string

            # ✅ Apply readonly styling if necessary
            if not details.get("edit", True):
                entry.configure(state="readonly", style="Readonly.TEntry")

            entry.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            self.fields[field] = entry  # ✅ Store reference to entry field

            row_index += 1  

        self.detail_frame_container.scrollable_frame.update_idletasks()  # ✅ Force UI refresh
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
        full_records = self.data_manager.fetch_all(self.entity_name)

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
        """ Saves a new entity record or updates an existing one. """
        form_data = self.get_form_data()

        if not form_data:
            print("❌ No data provided for saving.")
            return

        # ✅ Detect if cloned data is unchanged
        if hasattr(self, "cloned_data") and form_data == self.cloned_data:
            messagebox.showwarning(
                "Duplicate Clone Detected",
                "Please edit before saving. No changes detected from the cloned record."
            )
            return  # ✅ Prevent save operation

        selected_item = self.entity_tree.selection()
        primary_key_column = self.data_manager.get_primary_key(self.entity_name)

        if selected_item:
            # ✅ Updating an existing record
            selected_values = self.entity_tree.item(selected_item, "values")
            reference_column = self.tree_view_def["tree"]["columns"][0]
            reference_value = selected_values[0]

            # ✅ Fetch the actual row data
            full_records = self.data_manager.fetch_all(self.entity_name)
            matching_record = next(
                (record for record in full_records if str(record[reference_column]) == str(reference_value)), None
            )

            if not matching_record:
                print(f"❌ No matching record found for {reference_column}={reference_value}")
                return

            item_id = matching_record[primary_key_column]
            form_data[primary_key_column] = item_id  # ✅ Ensure ID is included in form_data

            try:
                self.data_manager.update_item(self.entity_name, form_data)
                print(f"✅ {self.entity_name} record updated.")
            except Exception as e:
                print(f"❌ Save Error: {e}")

        else:
            # ✅ Creating a new record
            try:
                self.data_manager.add_item(self.entity_name, form_data)
                print(f"✅ New {self.entity_name} record added.")
            except Exception as e:
                print(f"❌ Save Error: {e}")

        self.refresh_tree()
        if hasattr(self, "cloned_data"):
            del self.cloned_data  # ✅ Clear cloned data after saving

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
        """ Adds a new entity record to the database after validating data. """
        form_data = self.get_form_data()

        if not form_data:
            print("❌ No data provided for new item.")
            return

        try:
            # ✅ Validate form data before attempting insert
            self.validation_service.validate_form_data(self.entity_name, form_data)

            # ✅ Remove primary key for insert (handled by the database)
            primary_key_column = self.data_manager.get_primary_key(self.entity_name)
            if primary_key_column in form_data:
                del form_data[primary_key_column]  # ✅ Remove auto-increment primary key

            print(f"🔍 Insert Attempt: {form_data}")  # ✅ Debugging Output

            # ✅ Pass validated form data to `DatabaseService`
            self.data_manager.add_item(self.entity_name, form_data)

            print(f"✅ New {self.entity_name} record added.")

            self.refresh_tree()  # ✅ Refresh Treeview
            self.clear_form()  # ✅ Clear form after successful insert

        except ValueError as e:
            print(f"❌ Validation Error: {e}")
        except sqlite3.IntegrityError as e:
            print(f"❌ Database Integrity Error: {e}")
        except sqlite3.Error as e:
            print(f"❌ Database Error: {e}")

    def clone_item(self):
        """ Clones the selected entity record but does not save it immediately. """
        import tkinter.messagebox as messagebox  # ✅ Import messagebox for warning dialogs
        
        selected_item = self.entity_tree.selection()
        if not selected_item:
            print(f"❌ No item selected for cloning in {self.entity_name}.")
            return

        # ✅ Get the primary key column dynamically
        primary_key_column = self.data_manager.get_primary_key(self.entity_name)

        # ✅ Get selected row values
        selected_values = self.entity_tree.item(selected_item, "values")
        reference_column = self.tree_view_def["tree"]["columns"][0]  # First column is usually the primary key
        reference_value = selected_values[0]  # First column value should be the ID

        # ✅ Fetch full record data
        full_records = self.data_manager.fetch_all(self.entity_name)
        matching_record = next(
            (record for record in full_records if str(record[reference_column]) == str(reference_value)), None
        )

        if not matching_record:
            print(f"❌ No matching record found for {reference_column}={reference_value}")
            return

        # ✅ Clone data (EXCLUDE the primary key so user must save manually)
        self.cloned_data = {key: value for key, value in matching_record.items() if key != primary_key_column}

        # ✅ Populate the form with cloned data
        self.populate_detail_frame(prefill_data=self.cloned_data)  # ✅ Now correctly passing data

        print(f"✅ Cloned {self.entity_name} record: Original {primary_key_column}={reference_value}")
        print(f"🔹 Please edit before saving to avoid duplication.")

    def delete_item(self):
        """Deletes the selected item after confirmation and clears the form."""
        
        # ✅ Get the selected item from Treeview
        selected_item = self.entity_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No item selected for deletion.")
            return

        # ✅ Retrieve the primary key for the selected row
        primary_key_column = self.data_manager.get_primary_key(self.entity_name)
        
        selected_values = self.entity_tree.item(selected_item, "values")
        if not selected_values:
            messagebox.showerror("Error", "Selected item has no data.")
            return

        item_id = selected_values[0]  # ✅ Assuming the primary key is the first column in Treeview

        # ✅ Ask for confirmation before deleting
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
        if not confirm:
            return  # ✅ Exit if the user cancels

        try:
            # ✅ Call `delete_item` from `DatabaseService`
            self.data_manager.delete_item(self.entity_name, item_id)

            # ✅ Remove item from Treeview
            self.entity_tree.delete(selected_item)

            # ✅ Clear the form after successful deletion
            self.clear_form()

            print(f"✅ Deleted {self.entity_name} record with ID {item_id}")

        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Cannot delete item due to foreign key constraint: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An unexpected database error occurred: {e}")

    def clear_form(self):
        """ Clears all fields in the form after adding an item. """
        for field in self.fields.values():
            field.delete(0, tk.END)

    def get_form_data(self):
        """ Retrieves form data from input fields ensuring proper data types. """
        form_data = {}

        for field, entry in self.fields.items():
            value = entry.get().strip()  # ✅ Remove whitespace

            column_def = COLUMN_DEFINITIONS.get(self.entity_name, {}).get("columns", {}).get(field, {})

            # ✅ If field is primary key and no selection exists, skip it (assume auto-increment)
            if column_def.get("is_primary_key", False):
                selected_item = self.entity_tree.selection()
                if not selected_item:
                    continue  # ✅ Do not include the primary key for new records

            # ✅ Convert value to correct type
            expected_type = column_def.get("type")

            if value == "":
                value = column_def.get("default", None)  # ✅ Use default if provided, else None

            elif expected_type == "int":
                try:
                    value = int(value)
                except ValueError:
                    print(f"❌ Error: {field} expects an integer but got '{value}'")
                    return None

            elif expected_type == "float":
                try:
                    value = float(value)
                except ValueError:
                    print(f"❌ Error: {field} expects a float but got '{value}'")
                    return None

            form_data[field] = value

        return form_data

    def refresh_tree(self):
        """ Refreshes the treeview after an update. """
        self.entity_tree.delete(*self.entity_tree.get_children())  # Clear treeview
        self.populate_tree()  # Reload data

    def load_detail_image(self):
        """ 📷 IMAGE INTEGRATION: Loads and displays the entity image based on ImageID reference. """

        # 📷 Default ImageID for missing images
        DEFAULT_IMAGE_ID = 26

        # Determine which field to use: Assemblies use AssemImageID, Parts use ImageRef
        image_id = None
        if "AssemImageID" in self.item_data:
            image_id = self.item_data.get("AssemImageID")  # Assembly Image ID
        elif "ImageRef" in self.item_data:
            image_id = self.item_data.get("ImageRef")  # Part Image Reference

        # If no valid ImageID is found, use default ImageID
        if not image_id:
            image_id = DEFAULT_IMAGE_ID

        # 📷 Query the database to get the ImageFilename from the Images table
        query = "SELECT ImageFilename FROM Images WHERE ImageID = ?"
        result = self.db_service.fetch_one(query, (image_id,))

        # Use the retrieved filename or fallback to default.png
        image_filename = result[0] if result else "default.png"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)
        image_label = image_filename if result else "default.png"
        
        # 📷 Load image or fallback to default
        if not os.path.exists(image_path):
            image_path = os.path.join(IMAGE_FOLDER, "default.png")  # Fallback to default image

        try:
            img = Image.open(image_path)
            img = img.resize((400, 300), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)

            # 📷 Update label with new image
            self.image_label.config(image=img)
            self.image_label.image = img  # Keep reference to prevent garbage collection

        except Exception as e:
            print(f"Error loading image {image_path}: {e}")  # Log error for debugging


