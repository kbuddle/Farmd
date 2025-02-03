import tkinter as tk
from tkinter import ttk
from src.ui.ui_components import ScrollableFrame
from src.database.database_manager import DatabaseManager

class EntityForm(tk.Frame):
    def __init__(self, parent, entity_name, view_definition, data_manager, main_app):
        """
        Generic form for managing database entities like Parts, Drawings, etc.

        :param parent: Tkinter parent frame
        :param entity_name: Table name (e.g., "Parts", "Drawings")
        :param view_definition: Dictionary defining UI layout and fields
        :param data_manager: Database service instance
        """
        super().__init__(parent)
        self.entity_name = entity_name
        self.view_definition = view_definition
        self.data_manager = data_manager
        self.main_app = main_app
        self.create_widgets()
        self.populate_tree()

    def create_widgets(self):
        """Sets up the UI components including Treeview, Detail Frame, and Buttons."""
        # Grid configuration for layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Treeview frame expands
        self.grid_rowconfigure(1, weight=1)  # Detail frame expands
        self.grid_rowconfigure(2, weight=0)  # Button frame remains fixed

        # Top Section: Treeview with Scrollbar
        self.tree_frame_container = ttk.Frame(self)
        self.tree_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        self.entity_tree = ttk.Treeview(
            self.tree_frame_container,
            columns=list(self.view_definition["fields"].keys()),
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

        for field, details in self.view_definition["fields"].items():
            self.entity_tree.heading(field, text=details["label"])
            self.entity_tree.column(field, width=details["width"])

        self.entity_tree.bind("<<TreeviewSelect>>", self.load_entity_details)

        # Middle Section: Detail Frame
        self.detail_frame_container = ScrollableFrame(self, text=self.view_definition["detail_frame"]["text"])
        self.detail_frame_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.fields = {}
        for i, (field, details) in enumerate(self.view_definition["fields"].items()):
            ttk.Label(self.detail_frame_container.scrollable_frame, text=details["label"] + ":").grid(
                row=i, column=0, padx=5, pady=2, sticky="w"
            )
            entry = ttk.Entry(self.detail_frame_container.scrollable_frame, width=details["width"])
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            self.fields[field] = entry

        # Bottom Section: Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        for button_text, command_name in self.view_definition["button_frame"]["buttons"].items():
            if command_name == "show_landing_page":
                ttk.Button(self.button_frame, text=button_text, command=self.main_app.show_landing_page).pack(side=tk.LEFT, padx=5)
            elif hasattr(self, command_name):
                ttk.Button(self.button_frame, text=button_text, command=getattr(self, command_name)).pack(side=tk.LEFT, padx=5)
            else: 
                print(f"⚠️ Warning: Method '{command_name}' not found in {self.__class__.__name__}")

    def populate_tree(self):
        """Fetches and displays all records dynamically based on `entity_name`."""
        if hasattr(self.data_manager, "fetch_all"):
            entity_data = self.data_manager.fetch_all(self.entity_name)
            expected_columns = self.view_definition["fields"].keys()

            for record in entity_data:
                try:
                    values = tuple(record[col] for col in expected_columns)
                    self.entity_tree.insert("", "end", values=values)
                except KeyError as e:
                    print(f"❌ Missing column in fetched data: {e}")
        else:
            raise TypeError("Expected DatabaseService instance, got incorrect object type.")

    def load_entity_details(self, event):
        """Loads selected row details into the form fields."""
        selected_item = self.entity_tree.selection()
        if selected_item:
            entity_data = self.entity_tree.item(selected_item, "values")

            if len(entity_data) < len(self.view_definition["fields"].keys()):
                print("❌ Mismatch between expected and received columns.")
                return  

            for i, field in enumerate(self.view_definition["fields"].keys()):
                self.fields[field].delete(0, tk.END)
                self.fields[field].insert(0, entity_data[i])

    def save_entity(self):
        """Placeholder method for saving an entity."""
        pass

    def delete_entity(self):
        """Placeholder method for deleting an entity."""
        pass

    def clone_entity(self):
        """Placeholder method for cloning an entity."""
        pass

    def clear_form(self):
        """Clears the form fields."""
        for field in self.fields.values():
            field.delete(0, tk.END)
