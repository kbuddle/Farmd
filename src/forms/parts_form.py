import tkinter as tk
from tkinter import ttk, messagebox
from config.config_data import VIEW_DEFINITION
from src.ui.ui_components import ScrollableFrame

class PartsForm(tk.Tk):
    def __init__(self, view_definition):
        super().__init__()
        self.title(view_definition["title"])
        self.geometry(view_definition["geometry"])
        self.view_definition = view_definition
        
        # Upper section: Datasheet (Treeview) with Scrollbars
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        
        tree_config = self.view_definition["parts_tree"]
        self.parts_tree = ttk.Treeview(self.tree_frame, columns=tree_config["columns"], show=tree_config["show"],
                                       yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)
        
        for col in tree_config["columns"]:
            self.parts_tree.heading(col, text=tree_config["headings"][col])
            self.parts_tree.column(col, width=self.view_definition["fields"].get(col, {}).get("width", 130), anchor="w")
        
        self.tree_scroll_y.config(command=self.parts_tree.yview)
        self.tree_scroll_x.config(command=self.parts_tree.xview)
        
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.parts_tree.pack(fill=tk.BOTH, expand=True)
        self.parts_tree.bind(tree_config["bind_event"], self.load_part_details)
        
        # Lower section: Detail Card Frame using ScrollableFrame
        self.detail_frame_container = ScrollableFrame(self, text=self.view_definition["detail_frame"]["text"])
        self.detail_frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fields = {}
        for i, (field, details) in enumerate(self.view_definition["fields"].items()):
            ttk.Label(self.detail_frame_container.frame, text=details["label"] + ":").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            entry = ttk.Entry(self.detail_frame_container.frame, width=details["width"])
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fields[field] = entry
        
        # Buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for button_text, command_name in self.view_definition["button_frame"]["buttons"].items():
            ttk.Button(self.button_frame, text=button_text, command=getattr(self, command_name)).pack(side=tk.LEFT, padx=5)
    
    def load_part_details(self, event):
        selected_item = self.parts_tree.selection()
        if selected_item:
            part_data = self.parts_tree.item(selected_item, "values")
            for i, field in enumerate(self.view_definition["fields"].keys()):
                self.fields[field].delete(0, tk.END)
                self.fields[field].insert(0, part_data[i])
    
    def save_part(self):
        print("Saving part details")
        messagebox.showinfo("Info", "Part details saved.")
    
    def clone_part(self):
        print("Cloning part")
        messagebox.showinfo("Info", "Part cloned.")
    
    def delete_part(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this part?")
        if confirm:
            print("Deleting part")
            messagebox.showinfo("Info", "Part deleted.")
    
    def clear_form(self):
        for field in self.fields.values():
            field.delete(0, tk.END)
        print("Form cleared")
    
if __name__ == "__main__":
    app = PartsForm(VIEW_DEFINITION["PartsForm"])
    app.mainloop()
