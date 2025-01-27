from tkinter import Tk, ttk
from ui.notebook_manager import create_datasheet_tab
from core.query_builder import query_generator
from ui.ui_helpers import placeholder_add, placeholder_build, placeholder_clone, placeholder_delete, placeholder_edit, center_window_vertically

def main():
    root = Tk()
    root.title("FarmBot Management")

    # Define context for query generation
    contexts = {
        "Assemblies": {"title": "Manage Assemblies"}       
    }
    full_context = { 
        "Assemblies": {"title": "Manage Assemblies"},
        "Parts": {"title": "Manage Parts"},
        "Suppliers": {"title": "Manage Suppliers"},
        "Images": {"title": "Manage Images"},
        "Drawings": {"title": "Manage Drawings"}}
    contexts = contexts

    # Uncomment the following line if you want to center the window
    center_window_vertically(root, 1200, 600)

    # Create the main notebook widget
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Loop through the contexts and create a tab for each
    for context, settings in contexts.items():
        try:
            # Generate queries for the context
            queries = query_generator(context)

            # Create a datasheet tab for the context
            create_datasheet_tab(
                notebook,
                add_item=lambda: placeholder_add(context, None, queries["insert_query"], queries["fetch_query"]),
                edit_item=lambda: placeholder_edit(context, None, queries["fetch_query"], queries["update_query"], None),
                clone_item=lambda: placeholder_clone(context, None, queries["fetch_query"], queries["insert_query"], None),
                delete_item=lambda: placeholder_delete(context, None, queries["fetch_query"], queries["delete_query"]),
                build_assy=lambda assembly_id: placeholder_build(assembly_id) if context == "Assemblies" else None,
                context=context,
                fetch_query=queries["fetch_query"],
                insert_query=queries["insert_query"],
                update_query=queries["update_query"],
                delete_query=queries["delete_query"],
                max_width = 1400
            )
        except Exception as e:
            print(f"Failed to create tab for context '{context}': {e}")

    # Run the Tkinter main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
