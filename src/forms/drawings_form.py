import tkinter as tk
from tkinter import ttk
from src.ui.ui_components import ScrollableFrame
from src.database.database_manager import DatabaseManager
from main import MainApplication

class DrawingsForm(tk.Frame):
    def __init__(self, parent, view_definition, data_manager):
        super().__init__(parent)
        self.view_definition = view_definition
        self.data_manager = data_manager
        self.create_widgets()
        self.populate_drawing_tree()

    def create_widgets(self):
        # Use grid layout
        self.grid_columnconfigure(0, weight=1)  # Allow column expansion
        self.grid_rowconfigure(0, weight=1)  # Treeview frame should expand
        self.grid_rowconfigure(1, weight=1)  # Detail frame should expand
        self.grid_rowconfigure(2, weight=0)  # Button frame should remain fixed

        # Top Section: Treeview with Scrollbar
        self.tree_frame_container = ttk.Frame(self)
        self.tree_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Treeview
        self.drawing_tree = ttk.Treeview(
            self.tree_frame_container,
            columns=list(self.view_definition["fields"].keys()),
            show="headings"
        )
        
        # Scrollbars attached directly to Treeview
        tree_scroll_y = ttk.Scrollbar(self.tree_frame_container, orient="vertical", command=self.drawing_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.tree_frame_container, orient="horizontal", command=self.drawing_tree.xview)
        
        self.drawing_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Grid layout for proper positioning
        self.drawing_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Configure frame grid to expand properly
        self.tree_frame_container.grid_columnconfigure(0, weight=1)
        self.tree_frame_container.grid_rowconfigure(0, weight=1)
        
        for field, details in self.view_definition["fields"].items():
            self.drawing_tree.heading(field, text=details["label"])
            self.drawing_tree.column(field, width=details["width"])

        self.drawing_tree.bind("<<TreeviewSelect>>", self.load_drawing_details)

        # Middle Section: Detail Frame using ScrollableFrame
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

        # Bottom Section: Button Frame (Fixed at Bottom)
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)  # ✅ Always visible

        for button_text, command_name in self.view_definition["button_frame"]["buttons"].items():
            ttk.Button(self.button_frame, text=button_text, command=self.show_landing_page).pack(side=tk.LEFT, padx=5)

    def populate_drawing_tree(self):
        """Fetches and displays all parts dynamically based on VIEW_DEFINITION."""
        if hasattr(self.data_manager, "fetch_all"):  # ✅ Ensure it's a valid DatabaseService instance
            parts_data = self.data_manager.fetch_all("Drawings")  
            expected_columns = self.view_definition["fields"].keys()  # ✅ Dynamically get expected columns
            
            for part in parts_data:
                try:
                    values = tuple(part[col] for col in expected_columns)  # ✅ Fetch values dynamically
                    self.drawing_tree.insert("", "end", values=values)
                except KeyError as e:
                    print(f"❌ Missing column in fetched data: {e}")
        else:
            raise TypeError("Expected DatabaseService instance, got incorrect object type.")



    def load_drawing_details(self, event):
        selected_item = self.drawing_tree.selection()
        if selected_item:
            part_data = self.drawing_tree.item(selected_item, "values")
            print("Selected Part Data:", part_data)  # ✅ Debugging output

            if len(part_data) < len(self.view_definition["fields"].keys()):
                print("❌ Mismatch between expected and received columns.")
                return  # ✅ Prevents crash
        
            for i, field in enumerate(self.view_definition["fields"].keys()):
                self.fields[field].delete(0, tk.END)
                self.fields[field].insert(0, part_data[i])

    def save_drawing(self):
        # Placeholder method for saving a part
        pass

    def delete_drawing(self):
        # Placeholder method for deleting a drawing
        pass

    def clone_drawing(self):
        # Placeholder method for cloning a drawing
        pass

    def clear_form(self):
        # Placeholder method for clearing the form
        for field in self.fields.values():
            field.delete(0, tk.END)
