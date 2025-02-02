import tkinter as tk
from tkinter import messagebox, ttk

class CardView(tk.Frame):
    def __init__(self, parent, entity_data, config, save_callback=None, **kwargs):
        """
        A reusable UI component for displaying entity details in a structured card format.

        :param parent: The parent Tkinter widget.
        :param entity_data: Dictionary containing data for the selected entity.
        :param config: Configuration dictionary defining fields and visibility.
        :param save_callback: Function to call when saving/updating entity details.
        :param kwargs: Additional arguments for Tkinter Frame.
        """
        super().__init__(parent, **kwargs)
        
        self.entity_data = entity_data  # Data dictionary for the current entity
        self.config = config  # Field configuration dictionary
        self.save_callback = save_callback  # Function to trigger on save
        
        self.widgets = {}  # Store references to input fields
        self.create_ui()

    def create_ui(self):
        """Create UI elements dynamically based on the config."""
        for idx, (field, settings) in enumerate(self.config.items()):
            if settings.get("visible", True):  # Only show fields marked as visible
                label = tk.Label(self, text=settings.get("label", field))
                label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)

                if settings.get("editable", True):
                    entry = ttk.Entry(self)
                    entry.insert(0, str(self.entity_data.get(field, "")))
                    entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                    self.widgets[field] = entry
                else:
                    value_label = tk.Label(self, text=str(self.entity_data.get(field, "")))
                    value_label.grid(row=idx, column=1, sticky="w", padx=5, pady=2)
                    self.widgets[field] = value_label

        # Save Button
        save_button = ttk.Button(self, text="Save", command=self.save)
        save_button.grid(row=len(self.config), column=0, columnspan=2, pady=10)

    def save(self):
        """Save the updated data and trigger the callback."""
        updated_data = {field: widget.get() for field, widget in self.widgets.items() if isinstance(widget, ttk.Entry)}
        
        if self.save_callback:
            self.save_callback(updated_data)  # Call the external function
        
        print("Updated data:", updated_data)  # Debugging output

    def update_data(self, new_data):
        """Update the card's displayed data."""
        self.entity_data = new_data
        for field, widget in self.widgets.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, str(new_data.get(field, "")))
            else:
                widget.config(text=str(new_data.get(field, "")))

