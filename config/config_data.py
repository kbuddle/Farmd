import os
DEBUG = True

# ✅ Get absolute path of `config_data.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Move up **one level** to `src/`
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "src"))

# ✅ Set database path inside `src/database/`
DATABASE_PATH = os.path.join(SRC_DIR, "database", "Farmbot.db")
BACKUP_FOLDER = os.path.join(SRC_DIR, "database", "backups")

# Debugging output to confirm paths
print(f"✅ BASE_DIR: {BASE_DIR}")
print(f"✅ SRC_DIR: {SRC_DIR}")
print(f"✅ DATABASE_PATH: {DATABASE_PATH}")
print(f"✅ BACKUP_FOLDER: {BACKUP_FOLDER}")


COLUMN_DEFINITIONS = {
    "Assemblies": {
        "columns": {
            "AssemblyID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True},
            "AssemName": {"display_name": "Name", "width": 200, "type": "string"},
            "ParentAssemblyID": {"display_name": "Parent Assembly", "width": 100, "type": "int", "default": 40},
            "AssemImageRef": {"display_name": "Image Reference", "width": 150, "type": "string"},
            "AssemImage": {"display_name": "Image", "width": 150, "type": "blob", "admin": True},
            "AssemDwgID": {"display_name": "Drawing ID", "width": 200, "type": "int", "default": 266},
            "AssemCost": {"display_name": "Cost", "width": 80, "type": "numeric"},
            "AssemWeight": {"display_name": "Weight", "width": 80, "type": "numeric"},
            "AssemHoursParts": {"display_name": "Hours (Parts)", "width": 100, "type": "numeric", "default": 0},
            "AssemHoursAssembly": {"display_name": "Hours (Assembly)", "width": 100, "type": "numeric", "default": 0},
            "AssemTotalHours": {"display_name": "Total Hours", "width": 100, "type": "numeric", "admin": True},
            "AssemFocus": {"display_name": "Focus", "width": 100, "type": "string", "default": "Medium"},
            "AssemCostFlag": {"display_name": "Cost Flag", "width": 80, "type": "int", "default": 0},
            "AssemWeightFlag": {"display_name": "Weight Flag", "width": 80, "type": "int", "default": 0},
            "AssemStatus": {"display_name": "Status", "width": 100, "type": "string", "default": "Prelim"},
            "AssemNotes": {"display_name": "Notes", "width": 200, "type": "string"},
            "ProcurementType": {"display_name": "Procurement Type", "width": 100, "type": "string", "default": "Purchase"},
            "CreationDate": {"display_name": "Creation Date", "width": 120, "type": "string", "default": "2025-01-01", "admin": True},
            "LastUpdatedDate": {"display_name": "Last Updated Date", "width": 120, "type": "string", "default": "2025-01-01", "admin": True}
        }
    },
    "Parts": {
        "columns": {
            "PartID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True},
            "PartName": {"display_name": "Name", "width": 200, "type": "string", "parts": True},
            "Model": {"display_name": "Model", "width": 100, "type": "string", "parts": True},
            "Make": {"display_name": "Make", "width": 100, "type": "string", "parts": True},
            "Dimensions": {"display_name": "Dimensions", "width": 150, "type": "string", "parts": True},
            "Notes": {"display_name": "Notes", "width": 100, "type": "string", "parts": True},
            "Manufacturer": {"display_name": "Manufacturer", "width": 100, "type": "string", "parts": True},
            "ImageRef": {"display_name": "ImageRef", "width": 100, "type": "string"},
            "DrawingID": {"display_name": "DrawingID", "width": 100, "type": "int", "foreign_key": True, "default": 266},
            "ManPartNum": {"display_name": "ManPartNum", "width": 100, "type": "string", "parts": True},
            "ProcurementType": {"display_name": "ProcurementType", "width": 100, "type": "string", "default": "Purchase"},
            "PartWeight": {"display_name": "Weight", "width": 80, "type": "float", "default": 0},
            "PartMaterial": {"display_name": "Material", "width": 100, "type": "string"}
        }
    },
    "Suppliers": {
        "columns": {
            "SupplierID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True},
            "SupplierName": {"display_name": "Name", "width": 200, "type": "string"},
            "PricePerUnit": {"display_name": "Price/Unit", "width": 100, "type": "float", "default": 0.0},
            "PartID": {"display_name": "PartID", "width": 50, "type": "int", "foreign_key": True, "default": 50},
            "UnitOfOrder": {"display_name": "Unit of Order", "width": 100, "type": "string"},
            "WebRef": {"display_name": "Web URL", "width": 200, "type": "string"},
            "Manuf": {"display_name": "Manufacturer", "width": 100, "type": "string"},
            "ManPartNum": {"display_name": "Man. Part Num.", "width": 100, "type": "string"}
        }
    },
    "Drawings": {
        "columns": {
            "DrawingID": {"display_name": "ID", "width": 60, "type": "int", "is_primary_key": True},
            "DrawingName": {"display_name": "Name", "width": 200, "type": "string"},
            "DrawingPath": {"display_name": "Folder Path", "width": 250, "type": "string"},
            "Type": {"display_name": "Type", "width": 100, "type": "string"},
            "Date": {"display_name": "Date", "width": 120, "type": "string"},
            "Size": {"display_name": "Size", "width": 80, "type": "numeric"},
            "Status": {"display_name": "Status", "width": 100, "type": "string"},
            "Revision": {"display_name": "Revision", "width": 80, "type": "int"},
            "RelatedItemID": {"display_name": "Related PartID", "width": 100, "type": "int", "foreign_key": True, "default": 50}
        }
    },
    "Images": {
        "columns": {
            "ImageID": {"display_name": "ID", "width": 56, "type": "int", "is_primary_key": True},
            "ImageFileName": {"display_name": "File Name", "width": 200, "type": "string"},
            "ImageData": {"display_name": "BlobData", "width": 150, "type": "blob", "admin": True}
        }
    },
    "Assemblies_Parts": {
        "columns": {
            "ID": {"display_name": "ID", "width": 56, "type": "int", "is_primary_key": True},
            "ParentAssemblyID": {"display_name": "ParentAssemblyID", "width": 50, "type": "int"},
            "EntityType": {"display_name": "Entity Type", "width": 150, "type": "string"},
            "ProcurementType": {"display_name": "Procurement Type", "width": 100, "default": "Purchase"},
            "ChildAssemblyID": {"display_name": "ChildAssembly ID", "width": 60, "type": "int", "foreign_key": True },
            "PartID": {"display_name": "Part ID", "width": 60, "type": "int"},
            "Quantity": {"display_name": "Quantity", "width": 60, "type": "real"},
            "HoursParts": {"display_name": "Hours for Parts", "width": 60, "type": "real"},
            "HoursAssembly": {"display_name": "Hours to Assemble", "width": 60, "type": "real"},
            "TotalHours": {"display_name": "Total Hours", "width": 60, "type": "real"},
            "AssemFocus": {"display_name": "Focus", "width": 200, "type": "string"},
            "deleteFlag": {"display_name": "Delete Flag", "width": 200, "type": "string", "admin": True}
        }
    }
}
CONTEXTS ={
    "All": ["Assemblies", "Parts","Images", "Drawings", "Suppliers"],
    "Some": ["Assemblies"],    }

VIEW_DEFINITIONS = {
    "card_view": {
        "fields": ["AssemblyName", "ProcurementType", "Quantity", "TotalHours"],
        "order": ["AssemblyName", "ProcurementType", "Quantity", "TotalHours"]
    },
    "datasheet_view": {
        "fields": ["AssemblyName", "ProcurementType", "Quantity", "TotalHours", "Cost", "Weight"],
        "order": ["AssemblyName", "ProcurementType", "Quantity", "Cost", "Weight", "TotalHours"]
    },
    "detailed_view": {
        "fields": ["AssemblyName", "ProcurementType", "Quantity", "TotalHours", "Cost", "Weight", "Manufacturer"],
        "order": ["AssemblyName", "Manufacturer", "ProcurementType", "Quantity", "Cost", "Weight", "TotalHours"]
    }
}