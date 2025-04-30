# subject to redistribution within new filing structure.

import os

# The script assumes it is being run from the root folder
project_root = os.getcwd()  # Current directory (root)

# Define the expected folder and file structure
structure = {
    "config": {
        "settings.py": "General app settings (DB credentials, paths, etc.).",
        "logging_config.py": "Logging configuration setup.",
        "ui_config.py": "UI-related settings (themes, defaults)."
    },
    "src/core": {
        "app.py": "Entry point for the main application (initializes Tkinter).",
        "event_handlers.py": "Global event handling (button clicks, user actions).",
        "utilities.py": "General utility functions (formatting, conversions).",
        "constants.py": "Stores static values (labels, status codes)."
    },
    "src/database": {
        "db_instance.py": "Singleton DB instance and connection management.",
        "database_transactions.py": "Read, write, update, and delete operations.",
        "query_builder.py": "Functions to generate SQL queries dynamically.",
        "migrations.py": "Schema updates and database migrations."
    },
    "src/forms": {
        "base_form.py": "Parent class for all forms (modal windows, popups).",
        "assemblies_form.py": "Form for adding/editing assemblies.",
        "parts_form.py": "Form for adding/editing parts.",
        "supplier_form.py": "Form for adding/editing suppliers."
    },
    "src/models": {
        "assemblies_model.py": "Assembly data model class.",
        "parts_model.py": "Part data model class.",
        "suppliers_model.py": "Supplier data model class."
    },
    "src/ui": {
        "ui_components.py": "Reusable UI components (frames, buttons, modals).",
        "main_window.py": "Main application window layout.",
        "assemblies_ui.py": "UI layout for managing assemblies.",
        "parts_ui.py": "UI layout for managing parts.",
        "suppliers_ui.py": "UI layout for managing suppliers.",
        "ui_helpers.py": "Helper functions for layout adjustments, resizing."
    },
    "src/tests": {
        "test_database.py": "Tests for database operations.",
        "test_ui.py": "Tests for UI components.",
        "test_forms.py": "Tests for form logic."
    }
}

# Flatten expected files into a lookup set
expected_files = {
    os.path.join(project_root, folder, file) 
    for folder, files in structure.items() 
    for file in files
}

# Function to process files in the existing directory structure
def check_and_update_files(base_path, structure):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)

        # Skip folder creation if a file exists with the same name
        if os.path.exists(folder_path) and not os.path.isdir(folder_path):
            print(f"⚠️ Warning: {folder_path} exists as a file. Skipping folder creation.")
            continue

        os.makedirs(folder_path, exist_ok=True)  # Ensure folder exists

        for file, description in files.items():
            file_path = os.path.join(folder_path, file)

            # Ensure we're handling only files, not directories
            if os.path.isdir(file_path):
                print(f"⚠️ Skipping directory {file_path} (should be a file)")
                continue

            try:
                if os.path.exists(file_path):
                    # Read existing content
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Add description if missing at the top
                    if not lines or not lines[0].startswith("# "): 
                        lines.insert(0, f"# {description}\n\n")  

                    # Write back to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                else:
                    # Create new file with description
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"# {description}\n\n")

            except PermissionError as e:
                print(f"⚠️ Permission Denied: {file_path} - {e}")

# Function to mark unknown files for redistribution
def mark_unstructured_files(base_path):
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip non-Python files
            if not file.endswith(".py"):
                continue

            # If the file is not part of the expected structure
            if file_path not in expected_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Prepend redistribution note if not already present
                    if not lines or not lines[0].startswith("# subject to redistribution"):
                        lines.insert(0, "# subject to redistribution within new filing structure.\n\n")

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.writelines(lines)

                except PermissionError as e:
                    print(f"⚠️ Permission Denied: {file_path} - {e}")

# Execute functions
check_and_update_files(project_root, structure)
mark_unstructured_files(project_root)

print("✅ Project structure has been updated successfully!")
