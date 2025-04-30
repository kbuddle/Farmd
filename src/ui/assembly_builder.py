import tkinter as tk
from tkinter import ttk, messagebox
from database.database_manager import DatabaseManager
from ui.edit_component import EditComponentWindow
from models.assembly import Assembly

class AssemblyBuilder(tk.Toplevel):
    def __init__(self, parent, assembly_id):
        super().__init__(parent)
        self.title("Build Assembly")
        self.geometry("700x500")
        self.resizable(False, False)

        self.assembly = Assembly.fetch_from_db(assembly_id)  # ✅ Corrected call

        # Parts List Frame
        self.parts_frame = ttk.LabelFrame(self, text="Assigned Parts & Assemblies")
        self.parts_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.parts_tree = ttk.Treeview(self.parts_frame, columns=("ID", "Name", "Quantity"), show="headings")
        self.parts_tree.heading("ID", text="ID")
        self.parts_tree.heading("Name", text="Component")
        self.parts_tree.heading("Quantity", text="Quantity")
        self.parts_tree.pack(fill="both", expand=True)

        self.load_assigned_components()

        # Buttons
        self.edit_button = ttk.Button(self, text="Edit Component", command=self.open_edit_component)
        self.edit_button.pack(pady=5)

        self.remove_button = ttk.Button(self, text="Remove Component", command=self.remove_selected_component)
        self.remove_button.pack(pady=5)

    def load_assigned_components(self):
        """ Fetches assigned components for the selected assembly. """
        query = """
            SELECT p.PartID, p.PartName, ap.Quantity 
            FROM Assemblies_Parts ap
            JOIN Parts p ON ap.PartID = p.PartID
            WHERE ap.ParentAssemblyID = ?
        """
        db_manager = DatabaseManager()
        results = db_manager.execute_query(query, (self.assembly.item_id,))

        self.parts_tree.delete(*self.parts_tree.get_children())  # Clear existing rows
        for row in results:
            self.parts_tree.insert("", "end", values=row)

    def open_edit_component(self):
        """ Opens the EditComponentWindow for the selected row. """
        selected_item = self.parts_tree.selection()
        if not selected_item:
            return

        item_values = self.parts_tree.item(selected_item[0], "values")
        component_id, component_name, current_quantity = item_values[0], item_values[1], float(item_values[2])

        EditComponentWindow(self, self.assembly.item_id, component_id, component_name, current_quantity)

    def remove_selected_component(self):
        """ Removes the selected component from the assembly. """
        selected_item = self.parts_tree.selection()
        if not selected_item:
            return

        component_id = self.parts_tree.item(selected_item[0], "values")[0]
        self.assembly.remove_part(component_id)
        self.load_assigned_components()
