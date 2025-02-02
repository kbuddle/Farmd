# Form for adding/editing parts.

import tkinter as tk
from tkinter import ttk

class PartsForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parts Management")
        self.geometry("900x600")
        
        # Upper section: Datasheet (Treeview)
        self.parts_tree = ttk.Treeview(self, columns=("Part Name", "Part Number", "Model", "Make", "Dimensions"), show='headings')
        self.parts_tree.heading("Part Name", text="Part Name")
        self.parts_tree.heading("Part Number", text="Part Number")
        self.parts_tree.heading("Model", text="Model")
        self.parts_tree.heading("Make", text="Make")
        self.parts_tree.heading("Dimensions", text="Dimensions")
        self.parts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.parts_tree.bind("<ButtonRelease-1>", self.load_part_details)
        
        # Lower section: Detail Card Frame
        self.detail_frame = ttk.LabelFrame(self, text="Part Details")
        self.detail_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        self.fields = {}
        for i, field in enumerate(["Part Name", "Part Number", "Model", "Make", "Dimensions"]):
            ttk.Label(self.detail_frame, text=field + ":").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            entry = ttk.Entry(self.detail_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fields[field] = entry
        
        # Buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(self.button_frame, text="Save", command=self.save_part).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Clone", command=self.clone_part).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Delete", command=self.delete_part).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Cancel", command=self.clear_form).pack(side=tk.LEFT, padx=5)
    
    def load_part_details(self, event):
        selected_item = self.parts_tree.selection()
        if selected_item:
            part_data = self.parts_tree.item(selected_item, "values")
            for i, field in enumerate(self.fields):
                self.fields[field].delete(0, tk.END)
                self.fields[field].insert(0, part_data[i])
    
    def save_part(self):
        # Logic to save or update a part
        print("Saving part details")
    
    def clone_part(self):
        # Logic to duplicate a part record
        print("Cloning part")
    
    def delete_part(self):
        # Logic to delete the selected part
        print("Deleting part")
    
    def clear_form(self):
        for field in self.fields.values():
            field.delete(0, tk.END)
        print("Form cleared")
    
if __name__ == "__main__":
    app = PartsForm()
    app.mainloop()
