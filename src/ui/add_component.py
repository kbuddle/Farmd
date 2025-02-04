import tkinter as tk
from tkinter import ttk, messagebox
from src.database.database_manager import DatabaseManager
from src.models.assembly import Assembly

class AddComponentWindow(tk.Toplevel):
    def __init__(self, parent, assembly):
        super().__init__(parent)
        self.title("Add Existing Component")
        self.geometry("500x400")
        self.resizable(False, False)

        self.assembly = assembly
        self.db_manager = DatabaseManager()

        tk.Label(self, text="Select a component to add:", font=("Arial", 12, "bold")).pack(pady=5)

        # Table of available components
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Component Name")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_available_components()

        tk.Label(self, text="Enter Quantity:").pack()
        self.quantity_var = tk.StringVar(value="1.00")  # Default to 1.00
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, justify="center")
        self.quantity_entry.pack(pady=5)

        self.add_button = ttk.Button(self, text="Add Selected", command=self.add_selected_component)
        self.add_button.pack(pady=10)

    def load_available_components(self):
        """ Fetches available components for the selected assembly. """
        available = self.assembly.fetch_available_components()
        for row in available:
            self.tree.insert("", "end", values=row)

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

        quantity = round(quantity, 2)  # Ensure two decimal places

        component_id, component_name = self.tree.item(selected[0], "values")
        self.assembly.add_part(component_id, quantity)

        messagebox.showinfo("Success", f"{component_name} added to assembly with quantity {quantity}.")
        self.destroy()
