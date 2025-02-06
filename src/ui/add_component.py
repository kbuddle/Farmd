import tkinter as tk
from tkinter import ttk, messagebox
from database.database_manager import DatabaseManager
from models.assembly import Assembly
from services.assembly_parts_fetcher import AssemblyPartsFetcher

class AddComponentWindow(tk.Toplevel):
    def __init__(self, parent, assembly):
        super().__init__(parent)
        self.title("Add Existing Component")
        self.geometry("800x800")
        self.resizable(False, False)

        self.assembly = assembly
        self.db_manager = DatabaseManager()
        self.parts_fetcher = AssemblyPartsFetcher()  # ✅ Use new fetcher service

        tk.Label(self, text="Select a component to add:", font=("Arial", 12, "bold")).pack(pady=5)

        # Table of available components (Parts & Assemblies)
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Type"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Component Name")
        self.tree.heading("Type", text="Entity Type")  # ✅ Identifies Part or Assembly
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_available_components()

        tk.Label(self, text="Enter Quantity:").pack()
        self.quantity_var = tk.StringVar(value="1.00")  # Default to 1.00
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, justify="center")
        self.quantity_entry.pack(pady=5)

        self.add_button = ttk.Button(self, text="Add Selected", command=self.add_selected_component)
        self.add_button.pack(pady=10)

    def load_available_components(self):
        """ Fetches available parts and assemblies for selection. """
        available_items = self.parts_fetcher.fetch_available_items(self.assembly.item_id)

        self.tree.delete(*self.tree.get_children())  # Clear previous entries

        for row in available_items:
            self.tree.insert("", "end", values=(row["ID"], row["Name"], row["EntityType"]))

    def add_selected_component(self):
        """ Assigns the selected component to the assembly with specified quantity. """
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No Selection", "Please select a component to add.")
            return

        try:
            quantity = float(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a positive decimal number greater than zero.")
            return

        quantity = round(quantity, 2)  # ✅ Ensures two decimal places

        component_id, component_name, entity_type = self.tree.item(selected[0], "values")

        # ✅ Determine if it's a Part or an Assembly
        if entity_type == "Part":
            self.assembly.add_part(component_id, quantity)
        else:  # It's an Assembly
            self.assembly.add_assembly(component_id, quantity)  # Assuming add_assembly method exists

        messagebox.showinfo("Success", f"{component_name} ({entity_type}) added to assembly with quantity {quantity}.")
        self.destroy()
