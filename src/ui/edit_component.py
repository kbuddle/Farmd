import tkinter as tk
from tkinter import ttk, messagebox
from src.database.database_manager import DatabaseManager

class EditComponentWindow(tk.Toplevel):
    def __init__(self, parent, assembly_id, component_id, component_name, current_quantity):
        super().__init__(parent)
        self.title(f"Edit Component: {component_name}")
        self.geometry("350x200")
        self.resizable(False, False)

        self.assembly_id = assembly_id
        self.component_id = component_id

        tk.Label(self, text=f"Editing: {component_name}", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(self, text="Quantity:").pack()

        self.quantity_var = tk.StringVar(value=f"{current_quantity:.2f}")  # Ensure decimal formatting
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, justify="center")
        self.quantity_entry.pack(pady=5)

        self.save_button = ttk.Button(self, text="Save", command=self.save_changes)
        self.save_button.pack(pady=10)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def save_changes(self):
        """ Updates the quantity in the database and closes the window. """
        try:
            new_quantity = float(self.quantity_var.get())
            if new_quantity <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a positive decimal number greater than zero.")
            return

        new_quantity = round(new_quantity, 2)  # Ensure two decimal places

        db_manager = DatabaseManager()
        update_query = """
            UPDATE Assemblies_Parts 
            SET Quantity = ? 
            WHERE ParentAssemblyID = ? AND PartID = ?
        """
        db_manager.execute_query(update_query, (new_quantity, self.assembly_id, self.component_id), commit=True)

        messagebox.showinfo("Success", "Component quantity updated.")
        self.destroy()
