
import os
DEBUG = True

# ✅ Get absolute path of `config_data.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Move up **one level** to `src/`
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "src"))

# ✅ Set database path inside `src/database/`
DATABASE_PATH = os.path.join(SRC_DIR, "database", "Farmbot.db")
BACKUP_FOLDER = os.path.join(SRC_DIR, "database", "backups")
IMAGE_FOLDER = os.path.join(SRC_DIR, "images")

""" # Debugging output to confirm paths
print(f"✅ BASE_DIR: {BASE_DIR}")
print(f"✅ SRC_DIR: {SRC_DIR}")
print(f"✅ DATABASE_PATH: {DATABASE_PATH}")
print(f"✅ BACKUP_FOLDER: {BACKUP_FOLDER}") """


COLUMN_DEFINITIONS = {
    "Assemblies": {
        "columns": {
            "AssemblyID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True, "edit": False, "views": ["A1", "A2"]},
            "AssemName": {"display_name": "Name", "width": 200, "type": "string", "edit": True, "views": ["A1", "A2"]},
            "ParentAssemblyID": {"display_name": "ParentID", "width": 100, "type": "int", "edit": True, "foreign_key": True, "views": ["A1"], "default": 40},
            "AssemImageRef": {"display_name": "Image File", "width": 100, "type": "string", "edit": True, "views": ["A1", "A2"]},
            "AssemImageID": {"display_name": "ImageID", "width": 50, "type": "int", "edit": False, "foreign_key": True,"views": ["A1"], "default": 25},
            "AssemDwgID": {"display_name": "DrawingID", "width": 50, "type": "int", "edit": False, "foreign_key": True,"views": ["A1"], "default": 266},
            "AssemCost": {"display_name": "Cost", "width": 100, "type": "float", "edit": False, "views": ["A1"]},
            "AssemWeight": {"display_name": "Weight", "width": 100, "type": "float", "edit": False, "views": ["A1"]},
            "AssemHoursParts": {"display_name": "Part assemble hours", "width": 100, "type": "float", "edit": False, "views": ["A1"]},
            "AssemHoursAssembly": {"display_name": "Assembling hours", "width": 100, "type": "float", "edit": True, "views": ["A1"]},
            "AssemTotalHours": {"display_name": "Total hours", "width": 100, "type": "float",  "default": 266, "edit": True, "views": ["A1"]},
            "AssemFocus": {"display_name": "Focus", "width": 100, "type": "string", "edit": True, "views": ["A1"]},
            "AssemCostFlag": {"display_name": "Cost Flag", "width": 50, "type": "int", "edit": True, "views": ["A1"]},
            "AssemWeightFlag": {"display_name": "Weight Flag", "width": 50, "type": "int", "edit": True, "views": ["A1"]},
            "AssemStatus": {"display_name": "Status", "width": 100, "type": "string", "edit": True, "views": ["A1", "A2"]},
            "AssemNotes": {"display_name": "Notes", "width": 200, "type": "string", "edit": True, "views": ["A1", "A2"]},
            "ProcurementType": {"display_name": "ProcurementType", "width": 100, "type": "string", "default": "Purchase", "edit": False, "views": ["A1", "A2"]},
            "CreationDate": {"display_name": "Creation Date", "width": 100, "type": "string", "default": 0, "edit": False, "views": ["A1"]},
            "LastUpdatedDate": {"display_name": "Updated Date", "width": 100, "type": "string", "edit": False, "views": ["A1"]}
        }
    },"Parts": {
        "columns": {
            "PartID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True, "edit": False, "views": ["P1", "P2"]},
            "PartName": {"display_name": "Name", "width": 200, "type": "string", "edit": True, "views": ["P1", "P2"]},
            "Model": {"display_name": "Model", "width": 100, "type": "string", "edit": True, "views": ["P1", "P2"]},
            "Make": {"display_name": "Make", "width": 100, "type": "string", "edit": True, "views": ["P1"]},
            "Dimensions": {"display_name": "Dimensions", "width": 150, "type": "string", "edit": True, "views": ["P1", "P2"]},
            "Notes": {"display_name": "Notes", "width": 100, "type": "string", "edit": True, "views": ["P1"]},
            "Manufacturer": {"display_name": "Manufacturer", "width": 100, "type": "string", "edit": True, "views": ["P1"]},
            "ImageRef": {"display_name": "ImageRef", "width": 100, "type": "string", "edit": True, "views": ["P1", "I1"]},
            "DrawingID": {"display_name": "DrawingID", "width": 100, "type": "int", "foreign_key": True, "default": 266, "edit": True, "views": ["P1", "D1"]},
            "ManPartNum": {"display_name": "ManPartNum", "width": 100, "type": "string", "edit": True, "views": ["P1"]},
            "ProcurementType": {"display_name": "ProcurementType", "width": 100, "type": "string", "default": "Purchase", "edit": True, "views": ["P1"]},
            "PartWeight": {"display_name": "Weight", "width": 80, "type": "float", "default": 0, "edit": True, "views": ["P1"]},
            "PartMaterial": {"display_name": "Material", "width": 100, "type": "string", "edit": True, "views": ["P1"]}
        }
    },
    "Suppliers": {
        "columns": {
            "SupplierID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True, "edit": False, "views": ["S1", "S2"]},
            "SupplierName": {"display_name": "Name", "width": 200, "type": "string", "edit": True, "views": ["S1", "S2"]},
            "PricePerUnit": {"display_name": "Price/Unit", "width": 100, "type": "float", "default": 0.0, "edit": True, "views": ["S1"]},
            "PartID": {"display_name": "PartID", "width": 50, "type": "int", "foreign_key": True, "default": 50, "edit": True, "views": ["S1", "S2"]},
            "UnitOfOrder": {"display_name": "Unit of Order", "width": 100, "type": "string", "edit": True, "views": ["S1"]},
            "WebRef": {"display_name": "Web URL", "width": 200, "type": "string", "edit": True, "views": ["S1", "S2"]},
            "Manuf": {"display_name": "Manufacturer", "width": 100, "type": "string", "edit": True, "views": ["S1"]},
            "ManPartNum": {"display_name": "Man. Part Num.", "width": 100, "type": "string", "edit": True, "views": ["S1"]}
        }
    },
    "Drawings": {
        "columns": {
            "DrawingID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True, "edit": False, "views": ["D1", "D2"]},
            "DrawingName": {"display_name": "Name", "width": 200, "type": "string", "edit": True, "views": ["D1", "D2"]},
            "DrawingPath": {"display_name": "Folder Path", "width": 250, "type": "string", "edit": True, "views": ["D1", "D2"]},
            "Type": {"display_name": "Type", "width": 100, "type": "string", "edit": True, "views": ["D1", "D2"]},
            "Date": {"display_name": "Date", "width": 120, "type": "string", "edit": True, "views": ["D1"]},
            "Size": {"display_name": "Size", "width": 80, "type": "numeric", "edit": True, "views": ["D1"]},
            "Status": {"display_name": "Status", "width": 100, "type": "string", "edit": True, "views": ["D1"]},
            "Revision": {"display_name": "Revision", "width": 80, "type": "int", "edit": True, "views": ["D1"]},
            "RelatedItemID": {"display_name": "Related PartID", "width": 100, "type": "int", "foreign_key": True, "default": 50, "edit": True, "views": ["D1", "P1"]}
        }
    },
    "Images": {
        "columns": {
            "ImageID": {"display_name": "ID", "width": 56, "type": "int", "is_primary_key": True, "edit": False, "views": ["I1", "I2"]},
            "ImageFileName": {"display_name": "File Name", "width": 200, "type": "string", "edit": True, "views": ["I1", "I2"]}
        }
    },
    "Assemblies_Parts": {
        "columns": {
            "ID": {"display_name": "ID", "width": 56, "type": "int", "is_primary_key": True, "edit": False, "views": ["AP1", "AP2"]},
            "ParentAssemblyID": {"display_name": "ParentAssemblyID", "width": 50, "type": "int", "edit": True, "views": ["AP1"]},
            "EntityType": {"display_name": "Entity Type", "width": 150, "type": "string", "edit": False, "views": ["AP1"]},
            "ProcurementType": {"display_name": "Procurement Type", "width": 100, "default": "Purchase", "edit": True, "views": ["AP1"]},
            "ChildAssemblyID": {"display_name": "Child Assembly ID", "width": 60, "type": "int", "foreign_key": True, "default": 40, "edit": True, "views": ["AP1"]},
            "PartID": {"display_name": "Part ID", "width": 60, "type": "int", "edit": True, "views": ["AP1"]},
            "Quantity": {"display_name": "Quantity", "width": 60, "type": "real", "edit": True, "views": ["AP1"]},
            "HoursParts": {"display_name": "Hours for Parts", "width": 60, "type": "real", "edit": False, "views": ["AP1"]},
            "HoursAssembly": {"display_name": "Hours to Assemble", "width": 60, "type": "real", "edit": True, "views": ["AP1"]},
            "TotalHours": {"display_name": "Total Hours", "width": 60, "type": "real", "edit": False, "views": ["AP1"]},
            "AssemFocus": {"display_name": "Focus", "width": 200, "type": "string", "edit": True, "views": ["AP1"]},
            "deleteFlag": {"display_name": "Delete Flag", "width": 200, "type": "string", "admin": True, "edit": True, "views": ["AP1"]}
        }
    }
}

CONTEXTS ={
    "All": ["Assemblies", "Parts","Images", "Drawings", "Suppliers"],
    "Some": ["Assemblies"],    }



# Static properties for each view
STATIC_VIEW_DEFINITIONS = {
    "PartsForm": {
        "title": "Parts Management",
        "geometry": "900x800",
        "detail_frame": {"text": "Part Details"},
        "button_frame": {
            "buttons": {
                "Save": "save_item",
                "Clone": "clone_item",
                "Delete": "delete_item",
                "Back": "show_landing_page"
            }
        }
    },
    "DrawingsForm": {
        "title": "Drawings Management",
        "geometry": "900x800",
        "detail_frame": {"text": "Drawing Details"},
        "button_frame": {
            "buttons": {
                "Save": "save_item",
                "Clone": "clone_item",
                "Delete": "delete_item",
                "Back": "show_landing_page"
            }
        }
    },
    "ImagesForm": {
        "title": "Images Management",
        "geometry": "900x800",
        "detail_frame": {"text": "Image Details"},
        "button_frame": {
            "buttons": {
                "Save": "save_item",
                "Clone": "clone_item",
                "Delete": "delete_item",
                "Back": "show_landing_page"
            }
        }
    },
    "SuppliersForm1": {
        "title": "Suppliers Management",
        "geometry": "900x800",
        "detail_frame": {"text": "Supplier Details"},
        "button_frame": {
            "buttons": {
                "Save": "save_item",
                "Clone": "clone_item",
                "Delete": "delete_item",
                "Back": "show_landing_page"
            }
        }
    },
    "AssembliesForm": {
        "title": "Assemblies Management",
        "geometry": "900x800",
        "detail_frame": {"text": "Assembly Details"},
        "button_frame": {
            "buttons": {
                "Save": "save_item",
                "Clone": "clone_item",
                "Delete": "delete_item",
                "Back": "show_landing_page"
            }
        }
    }
}
def derive_view_definitions(column_definitions, static_definitions):
    """
    Generates VIEW_DEFINITIONS dynamically by merging predefined UI settings with 
    dynamically assigned columns and headings. Also ensures correct view mappings and 
    includes the 'edit' flag from COLUMN_DEFINITIONS.

    :param column_definitions: Dictionary containing column metadata.
    :param static_definitions: Predefined UI configurations for each form.
    :return: A dictionary containing fully constructed VIEW_DEFINITIONS.
    """
    view_definitions = {}

    # Define valid view prefixes for each entity type
    valid_view_prefixes = {
        "Parts": "P",
        "Drawings": "D",
        "Suppliers": "S",
        "Images": "I",
        "Assemblies_Parts": "AP",
        "Assemblies": "A"
    }

    # Iterate over column definitions to generate view-specific configurations
    for table_name, table_data in column_definitions.items():
        valid_prefix = valid_view_prefixes.get(table_name, "")  # Ensure only valid views are assigned

        for column_name, column_attrs in table_data["columns"].items():
            if "views" in column_attrs:
                for view in column_attrs["views"]:
                    # Ensure that only valid views are assigned to the correct entity
                    if not view.startswith(valid_prefix):
                        continue  # Skip mismatched views (e.g., avoid PartsFormI1)

                    # Define a unique view name based on the entity and view key
                    view_name = f"{table_name}Form{view}"  # e.g., "PartsFormP1"

                    # Ensure this view exists in the definitions
                    if view_name not in view_definitions:
                        view_definitions[view_name] = {
                            "title": f"{table_name} Management ({view})",
                            "geometry": "900x800",
                            "detail_frame": {"text": f"{table_name} Details"},
                            "button_frame": {
                                "buttons": {
                                    "Save": "save_item",
                                    "Clone": "clone_item",
                                    "Delete": "delete_item",
                                    "Back": "show_landing_page"
                                }
                            },
                            "tree": {"columns": [], "headings": {}, "show": "headings", "bind_event": "<ButtonRelease-1>"},
                            "fields": {}
                        }

                    # Append column details dynamically, including 'edit' flag
                    view_definitions[view_name]["tree"]["columns"].append(column_name)
                    view_definitions[view_name]["tree"]["headings"][column_name] = column_attrs.get("display_name", column_name)
                    view_definitions[view_name]["fields"][column_name] = {
                        "label": column_attrs.get("display_name", column_name),
                        "width": column_attrs.get("width", 100),
                        "edit": column_attrs.get("edit", True)  # Default to True if not specified
                    }

    return view_definitions


# Generate final VIEW_DEFINITIONS
VIEW_DEFINITIONS = derive_view_definitions(COLUMN_DEFINITIONS, STATIC_VIEW_DEFINITIONS)

""" # Debugging output
import pprint
pprint.pprint(VIEW_DEFINITIONS) """


