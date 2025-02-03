import tkinter as tk
from tkinter import ttk
from src.ui.ui_components import ScrollableFrame
from src.database.data_manager import DataManager

class PartsForm(tk.Frame):
    def __init__(self, parent, view_definition, data_manager):
        super().__init__(parent)
        self.view_definition = view_definition
        self.data_manager = data_manager
        self.create_widgets()
        self.populate_parts_tree()

    def create_widgets(self):
        # Initialize parts_tree
        self.parts_tree = ttk.Treeview(self, columns=list(self.view_definition["fields"].keys()), show='headings')
        self.parts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for field, details in self.view_definition["fields"].items():
            self.parts_tree.heading(field, text=details["label"])
            self.parts_tree.column(field, width=details["width"])

        self.parts_tree.bind("<<TreeviewSelect>>", self.load_part_details)

        # Lower section: Detail Card Frame using ScrollableFrame
        self.detail_frame_container = ScrollableFrame(self, text=self.view_definition["detail_frame"]["text"])
        self.detail_frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fields = {}
        for i, (field, details) in enumerate(self.view_definition["fields"].items()):
            ttk.Label(self.detail_frame_container.scrollable_frame, text=details["label"] + ":").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            entry = ttk.Entry(self.detail_frame_container.scrollable_frame, width=details["width"])
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fields[field] = entry
        
        # Buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for button_text, command_name in self.view_definition["button_frame"]["buttons"].items():
            ttk.Button(self.button_frame, text=button_text, command=getattr(self, command_name)).pack(side=tk.LEFT, padx=5)

    def populate_parts_tree(self):
        # Fetch data from the database
        parts_data = self.data_manager.fetch_all_parts()  # Use the fetch_all_parts method from DataManager
        for part in parts_data:
            self.parts_tree.insert("", tk.END, values=part)

    def load_part_details(self, event):
        selected_item = self.parts_tree.selection()
        if selected_item:
            part_data = self.parts_tree.item(selected_item, "values")
            for i, field in enumerate(self.view_definition["fields"].keys()):
                self.fields[field].delete(0, tk.END)
                self.fields[field].insert(0, part_data[i])

    def save_part(self):
        # Placeholder method for saving a part
        pass

    def delete_part(self):
        # Placeholder method for deleting a part
        pass

    def clone_part(self):
        # Placeholder method for cloning a part
        pass

    def clear_form(self):
        # Placeholder method for clearing the form
        for field in self.fields.values():
            field.delete(0, tk.END)
    
if __name__ == "__main__":
    root = tk.Tk()
    view_definition = {
        "fields": {
            "part_name": {"label": "Part Name", "width": 100},
            "description": {"label": "Description", "width": 200},
            "category": {"label": "Category", "width": 100},
        },
        "detail_frame": {"text": "Part Details"},
        "button_frame": {"buttons": {"Save": "save_part", "Delete": "delete_part"}}
    }
    db_path = "path/to/your/database.db"  # Adjust the path to your database
    data_manager = DataManager(db_path)
    app = PartsForm(root, view_definition, data_manager)
    app.pack(fill="both", expand=True)
    root.mainloop()
