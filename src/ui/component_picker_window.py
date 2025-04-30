import tkinter as tk
from tkinter import ttk, messagebox
from services.assembly_parts_fetcher import AssemblyPartsFetcher
from config.config_data import VIEW_DEFINITIONS, get_ap3_field_mapping

class ComponentPickerWindow(tk.Toplevel):
    """UI window for selecting components (Parts or Assemblies) to assign to an assembly."""

    def __init__(self, parent, assembly_id, assign_callback, db_service, view_name="assemblies_parts_view"):
        super().__init__(parent)
        self.parent = parent
        self.assembly_id = assembly_id
        self.assign_callback = assign_callback
        self.db_service = db_service

        self.title("Component Picker Window")
        self.geometry("600x400")  # Adjust window size as needed

        # ✅ Initialize the treeview **BEFORE** populating data
        self.tree = ttk.Treeview(self)  
        self.tree.pack(fill="both", expand=True)

        # Populate the available components
        self.populate_available_components()

    def get_valid_columns(self):
        return {"PartID", "PartName", "EntityType", "Dimensions", "Model", "Make", "Manufacturer", "ProcurementType"}

    def create_widgets(self):
        """Creates UI elements dynamically based on view definitions."""
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.populate_available_components())

        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)

        self.component_list = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.component_list.heading(col, text=col)
        self.component_list.pack()
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Update the command to use the callback function provided via `add_callback`
        self.assign_button = ttk.Button(button_frame, text="Assign Component", command=self.handle_component_selection, style="success.TButton")
        self.assign_button.pack(side="left", expand=True, padx=5)

        self.commit_button = ttk.Button(button_frame, text="Commit Quantities", command=self.commit_quantities, style="primary.TButton")
        self.commit_button.pack(side="left", expand=True, padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy, style="danger.TButton")
        self.cancel_button.pack(side="right", expand=True, padx=5)

    def populate_available_components(self):
        """Populates the component selection table dynamically based on config mappings."""
        
        # 1️⃣ Fetch full column mapping
        column_mapping = get_ap3_field_mapping()  
        print("Raw Column Mapping:", column_mapping)  # Debugging Output

        # 2️⃣ Extract only field names (keys) for Treeview columns
        field_names = list(column_mapping.keys())  # Extract keys only
        self.tree["columns"] = field_names

         # ✅ Fix: Hide phantom first column
        self.tree.column("#0", width=0, stretch=tk.NO)  
        self.tree.heading("#0", text="")  

        # 3️⃣ Set table headings using extracted field names (not SQL expressions)
        for col_key in field_names:
            self.tree.heading(col_key, text=col_key)  # Use actual dictionary key as heading
            self.tree.column(col_key, width=120)  

        # 4️⃣ Fetch available parts dynamically
        fetcher = AssemblyPartsFetcher(self.db_service)
        parts_list = fetcher.fetch_available_items(self.assembly_id)

        print("Fetched Parts:", parts_list)  # Debugging Output

        # 5️⃣ Insert dictionary data correctly
        for part in parts_list:
            values = [part.get(col_key, "N/A") for col_key in field_names]  # Use extracted field names
            self.tree.insert("", "end", values=values)


    def sort_table(self, column):
        """Sorts the Treeview table by the selected column."""
        items = [(self.component_list.set(item, column), item) for item in self.component_list.get_children()]
        items.sort()
        for index, (_, item) in enumerate(items):
            self.component_list.move(item, "", index)

    def commit_quantities(self):
        """Commits assigned components with their edited quantities and units."""
        for item in self.component_list.get_children():
            component_data = self.component_list.item(item)
            component_id = component_data["values"].get("ID", None)  # Accessing via dictionary
            quantity = float(component_data["values"].get("Quantity", 1))
            unit = component_data["values"].get("Unit", "each")
            self.add_callback(component_id, quantity, unit)
        self.destroy()

    def handle_component_selection(self):
        """Retrieves the selected component and triggers the assignment to the assembly."""
        selected_item = self.component_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No component selected to assign.")
            return

        # Extract component details using dictionary-based lookup
        component_data = self.component_list.item(selected_item[0])  # This is a dictionary
        component_values = component_data["values"]

        # Ensure valid data exists
        component_id = component_values.get("ID", None)
        entity_type = component_values.get("EntityType", None)

        if component_id is None or entity_type is None:
            messagebox.showerror("Error", "Missing required component data.")
            return

        # Ensure the entity_type is valid (either Part or Assembly)
        if entity_type not in ["Part", "Assembly"]:
            messagebox.showerror("Error", f"Invalid EntityType: {entity_type}.")
            return

        # Call the callback function (provided via the constructor) to assign the component
        self.add_callback(component_id, entity_type)

        # Refresh UI
        self.populate_available_components()
