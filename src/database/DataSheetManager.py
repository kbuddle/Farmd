import tkinter as tk
from tkinter import ttk, Frame, Button, messagebox
from src.database.operations import DatabaseOperations  # ✅ Uses DatabaseOperations for DB actions

class DatasheetManager:
    """Manages UI components and connects UI with database operations."""

    def __init__(self, parent, context_name, db_path):
        """
        Initializes the DatasheetManager.

        Args:
            parent (tk.Widget): The parent container.
            context_name (str): The entity type (e.g., "Assemblies", "Parts").
            db_path (str): Path to the database file.
        """
        self.parent = parent
        self.context_name = context_name
        self.db_ops = DatabaseOperations(db_path)  # ✅ Calls DatabaseOperations directly

        self.tab_frame = self._create_datasheet_tab()

    def _create_datasheet_tab(self):
        """Creates a tab with a data table and buttons."""
        tab_frame = tk.Frame(self.parent)
        tab_frame.pack(fill="both", expand=True)

        self.create_buttons_frame(tab_frame)
        self.create_datasheet_view(tab_frame)

        return tab_frame

    def create_buttons_frame(self, parent_frame):
        """Creates CRUD buttons."""
        button_frame = Frame(parent_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        def create_button(text, command):
            return Button(button_frame, text=text, command=command).pack(side="left", padx=10, pady=10)

        create_button(f"Add {self.context_name}", self.add_item)
        create_button(f"Edit {self.context_name}", self.edit_item)
        create_button(f"Clone {self.context_name}", self.clone_item)
        create_button(f"Delete {self.context_name}", self.delete_item)

    def create_datasheet_view(self, parent_widget):
        """Creates a UI table (Treeview) to display items."""
        table_frame = Frame(parent_widget, width=1000, height=600)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.treeview = ttk.Treeview(table_frame, columns=("ID", "Name"), show="headings", selectmode="browse")
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Name", text="Name")

        self.treeview.pack(fill="both", expand=True)

        self.populate_table()

    def populate_table(self):
        """Fetches and displays data from the database."""
        self.treeview.delete(*self.treeview.get_children())
        rows = self.db_ops.fetch_all(self.context_name)  # ✅ Calls DatabaseOperations
        for row in rows:
            self.treeview.insert("", "end", values=row)

    def add_item(self):
        """Handles adding an item via DatabaseOperations."""
        data = {}  # Replace with actual form data
        new_id = self.db_ops.add_item(self.context_name, data)
        if new_id != -1:
            messagebox.showinfo("Success", "Item added successfully!")
            self.populate_table()

    def edit_item(self):
        """Handles editing an item."""
        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected for editing.")
            return

        item_id = self.treeview.item(selected_item)['values'][0]
        updated_data = {}  # Replace with actual form data
        if self.db_ops.update_item(self.context_name, item_id, updated_data):
            messagebox.showinfo("Success", "Item updated successfully!")
            self.populate_table()

    def clone_item(self):
        """Handles cloning an item."""
        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected for cloning.")
            return

        item_id = self.treeview.item(selected_item)['values'][0]
        cloned_id = self.db_ops.clone_item(self.context_name, item_id)
        if cloned_id != -1:
            messagebox.showinfo("Success", "Item cloned successfully!")
            self.populate_table()

    def delete_item(self):
        """Handles deleting an item."""
        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected for deletion.")
            return

        item_id = self.treeview.item(selected_item)['values'][0]
        if self.db_ops.delete_item(self.context_name, item_id):
            messagebox.showinfo("Success", "Item deleted successfully!")
            self.populate_table()
