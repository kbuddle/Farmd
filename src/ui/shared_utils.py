# subject to redistribution within new filing structure.

import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports

from config.config_data import DEBUG, COLUMN_DEFINITIONS, DATABASE_PATH
from src.database.transaction import DatabaseTransactionManager

from config.config_data import COLUMN_DEFINITIONS, DEBUG



# Dictionary to track the current sort direction for each column
sort_directions = {}

def sort_table(treeview, column, reverse):
    """
    Sorts the Treeview table by a specified column.

    Args:
        treeview (ttk.Treeview): The table to sort.
        column (str): The column to sort by.
        reverse (bool): Sorting direction (ascending/descending).
    """
    try:
        # Fetch all values
        data = [(treeview.set(item, column), item) for item in treeview.get_children()]
        
        # Check if sorting is numeric
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0], reverse=reverse)  # Sort as string if not numeric

        for index, (val, item) in enumerate(data):
            treeview.move(item, "", index)

        # Toggle reverse sorting
        treeview.heading(column, command=lambda: sort_table(treeview, column, not reverse))

    except Exception as e:
        print(f"ERROR: Sorting failed for column {column}. {e}")


def populate_table(treeview, fetch_query, params=None, debug=True): 
    """
    Populates the Treeview with data from the database.
    """
    if debug:
        print(f"🔍 DEBUG: Fetch Query = {fetch_query}, Params = {params}")

    try:
        # ✅ Fetch results from database
        rows = self.que.execute_query(fetch_query, params=params, debug=debug)

        # ✅ Print fetched rows for debugging
        print(f"✅ DEBUG: Query returned {len(rows)} rows")

        # ✅ Clear existing rows in the Treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        # ✅ Insert rows into the Treeview
        for row in rows:
            treeview.insert("", "end", values=list(row.values()))

    except Exception as e:
        print(f"❌ ERROR in populate_table: {e}")

