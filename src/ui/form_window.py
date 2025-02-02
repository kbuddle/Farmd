import tkinter as tk
from tkinter import messagebox, ttk

class FormWindow:
    """ Creates a dynamic UI form with Save and Cancel buttons. """

    def __init__(self, title, fields, on_save_callback, initial_data=None):
        """
        Initializes the form window.

        Args:
            title (str): The title of the form window.
            fields (dict): Dictionary of form fields.
            on_save_callback (callable): Function to execute on save.
        """
        self.window = tk.Toplevel()
        self.window.title(title)
        self.entries = {}

        # Create form fields dynamically
        for i, (field_name, field_details) in enumerate(fields.items()):
            tk.Label(self.window, text=field_name).grid(row=i, column=0, padx=5, pady=5)
            
            entry_var = tk.StringVar()
            entry_widget = tk.Entry(self.window, textvariable=entry_var)
            
            # Populate default values if provided
            if initial_data and field_name in initial_data:
                entry_var.set(initial_data[field_name])
                        
            entry_widget.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field_name] = entry_var

        # Add Save and Cancel buttons
        self.add_buttons(on_save_callback)

    def add_buttons(self, on_save_callback):
        """ Adds Save and Cancel buttons to the form. """
        save_button = tk.Button(self.window, text="Save", command=lambda: self.save_form(on_save_callback), bg="green", fg="white")
        save_button.grid(row=len(self.entries) + 1, column=0, padx=5, pady=5, sticky="w")

        cancel_button = tk.Button(self.window, text="Cancel", command=self.window.destroy, bg="red", fg="white")
        cancel_button.grid(row=len(self.entries) + 1, column=1, padx=5, pady=5, sticky="e")

    def save_form(self, on_save_callback):
        """ Collects form data and passes it to the save callback. """
        form_data = {field: var.get() for field, var in self.entries.items()}
        on_save_callback(form_data)


