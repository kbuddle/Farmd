import tkinter as tk
from tkinter import messagebox
from src.database.query_generator import QueryGenerator  # Ensure no circular imports

class UIHelpers:
    """Handles UI notifications separately from database logic."""

    @staticmethod
    def show_error(title, message):
        """Displays an error message in a popup."""
        messagebox.showerror(title, message)

    @staticmethod
    def show_info(title, message):
        """Displays an informational message in a popup."""
        messagebox.showinfo(title, message)

    @staticmethod
    def ask_confirmation(title, message):
        """Asks user for confirmation and returns True/False."""
        return messagebox.askyesno(title, message)


class ButtonFrame:
    """Encapsulates the logic for creating a reusable frame with CRUD buttons."""

    def __init__(self, parent_frame, context, on_add, on_edit, on_clone, on_delete, build_assy=None):
        """
        Initializes a button frame for CRUD operations.

        Args:
            parent_frame (tk.Frame): Parent frame to place the buttons.
            context (str): The entity type (e.g., "Assemblies", "Parts").
            on_add (function): Function to handle item addition.
            on_edit (function): Function to handle item editing.
            on_clone (function): Function to handle item cloning.
            on_delete (function): Function to handle item deletion.
            build_assy (function, optional): Extra function (e.g., for building assemblies).
        """
        self.context = context
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_clone = on_clone
        self.on_delete = on_delete
        self.build_assy = build_assy

        self.frame = tk.Frame(parent_frame)
        self.frame.pack(fill="x", padx=10, pady=5)

        # ✅ Lazy Instantiation of QueryGenerator to Avoid Circular Imports
        self.query_gen = None  

        # Create buttons
        self._create_buttons()

    def _create_buttons(self):
        """Creates and places the CRUD buttons in the frame."""
        self.query_gen = QueryGenerator(self.context)  # Instantiated here to avoid import loops
        queries = self.query_gen.get_all_queries()

        self._create_button(f"Add {self.context}", lambda: self.on_add(self.context, queries["insert_query"], queries["fetch_query"]), "green")
        self._create_button(f"Edit {self.context}", lambda: self.on_edit(self.context, queries["fetch_query"], queries["update_query"]), "blue")
        self._create_button(f"Clone {self.context}", lambda: self.on_clone(self.context), "orange")
        self._create_button(f"Delete {self.context}", lambda: self.on_delete(self.context), "red")

        if self.build_assy:
            self._create_button(f"Build {self.context}", self.build_assy, "purple")

    def _create_button(self, text, command, bg="lightgray"):
        """Creates a single button and adds it to the frame."""
        btn = tk.Button(self.frame, text=text, command=command, bg=bg, fg="black", padx=10, pady=5)
        btn.pack(side="left", padx=5, pady=5)
