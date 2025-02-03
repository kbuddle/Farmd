import tkinter as tk
from tkinter import ttk
from src.ui.ui_components import ScrollableFrame
from src.database.database_manager import DatabaseManager

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

        # ✅ Top Section: Treeview with Scrollbar (Uses P2)
        self.tree_frame_container = ttk.Frame(self)
        self.tree_frame_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # ✅ Use tree_view_def for defining tree columns
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

        # ✅ Use tree_view_def for setting column names
        for field, details in self.tree_view_def["tree"]["headings"].items():
            self.entity_tree.heading(field, text=details)
            self.entity_tree.column(field, width=100)  # Default width

        self.entity_tree.bind("<<TreeviewSelect>>", self.load_entity_details)

        # ✅ Middle Section: Detail Frame (Uses P1)
        self.detail_frame_container = ScrollableFrame(self, text=self.detail_view_def["detail_frame"]["text"])
        self.detail_frame_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # ✅ Bottom Section: Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        for button_text, command_name in self.detail_view_def["button_frame"]["buttons"].items():
            if command_name == "show_landing_page":
                ttk.Button(self.button_frame, text=button_text, command=self.main_app.show_landing_page).pack(side=tk.LEFT, padx=5)
            elif hasattr(self, command_name):
                ttk.Button(self.button_frame, text=button_text, command=getattr(self, command_name)).pack(side=tk.LEFT, padx=5)
            else: 
                print(f"⚠️ Warning: Method '{command_name}' not found in {self.__class__.__name__}")


    def populate_tree(self):
        """Fetches and displays all parts dynamically based on tree_view_def (P2)."""
        from config.config_data import COLUMN_DEFINITIONS  # ✅ Ensure columns_definition is imported

        if not hasattr(self.data_manager, "fetch_all"):
            raise TypeError("Expected DatabaseService instance, got incorrect object type.")
        
        tree_columns = self.tree_view_def.get("tree", {}).get("columns", [])  # ✅ Now references P2
        if not tree_columns:
            raise ValueError(f"Tree columns are missing in view definition for {self.entity_name}")

        tree_columns_sql = ", ".join(tree_columns)  # ✅ Format for SQL query
        
        query = f"SELECT {tree_columns_sql} FROM {self.entity_name}"  # ✅ Fetch limited fields
        print(f"Here is the query for all relevant data: {query}")
        
        entity_data = self.data_manager.db_manager.execute_query(query)

        for record in entity_data:
            values = tuple(record[col] for col in tree_columns)
            self.entity_tree.insert("", "end", values=values)


    

    def populate_detail_frame(self):
        """Fetch all columns dynamically from the database and update the detail frame using detail_view_def (P1)."""
        from config.config_data import COLUMN_DEFINITIONS  

        self.fields = {}  # ✅ Clear previous fields
        row_index = 0  

        entry_style = ttk.Style()
        entry_style.configure("Readonly.TEntry", foreground="black", background="lightgray")  # ✅ Styling for readonly fields

        for field, details in self.detail_view_def["fields"].items():
            ttk.Label(self.detail_frame_container.scrollable_frame, text=details["label"] + ":").grid(
                row=row_index, column=0, padx=5, pady=2, sticky="w"
            )

            entry = ttk.Entry(self.detail_frame_container.scrollable_frame, width=details["width"])
            if not details.get("edit", True):  # ✅ Apply readonly style if field is not editable
                entry.configure(state="readonly", style="Readonly.TEntry")  

            entry.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            self.fields[field] = entry

            row_index += 1  


            
    def load_entity_details(self, event):
        """Loads selected row details into the form fields, ensuring readonly fields are updated."""
        
        selected_item = self.entity_tree.selection()
        if not selected_item:
            return  # ✅ Exit if nothing is selected

        selected_values = self.entity_tree.item(selected_item, "values")
        primary_key_column = self.view_definition.get("primary_key", "id")  # ✅ Ensure we fetch by the correct primary key
        
        primary_key_value = selected_values[0]  # ✅ Assuming first column is the primary key
        query = f"SELECT * FROM {self.entity_name} WHERE {primary_key_column} = ?"  # ✅ Fetch all columns for this row
        
        full_record = self.data_manager.db_manager.execute_query(query, (primary_key_value,))
        
        if not full_record:
            print(f"❌ No matching record found for {primary_key_column}={primary_key_value}")
            return  

        entity_data = full_record[0]  # ✅ Get the first (and only) matching row

        for column_name, entry_widget in self.fields.items():
            entry_widget.configure(state="normal")  # ✅ Temporarily enable entry for updating
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, entity_data[column_name])  # ✅ Now uses full database data
            if column_name in self.view_definition["fields"] and self.view_definition["fields"][column_name].get("edit", True):
                entry_widget.configure(state="readonly")  # ✅ Restore readonly state

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
