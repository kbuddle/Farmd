import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports

from config.config_data import DEBUG, DATABASE, COLUMN_DEFINITIONS
from core.database_transactions import DatabaseTransactionManager

from config.config_data import COLUMN_DEFINITIONS, DEBUG


db_manager = DatabaseTransactionManager(DATABASE)

# Dictionary to track the current sort direction for each column
sort_directions = {}

def sort_table(treeview, column, fetch_query):
    """
    Sorts the Treeview data by the given column in alternating order (ASC/DESC).

    Args:
        treeview (ttk.Treeview): The Treeview widget to sort.
        column (str): The column to sort.
        fetch_query (str): SQL query to fetch data.
    """
    global sort_directions

    # Determine the current sort direction for the column
    current_direction = sort_directions.get(column, "ASC")
    next_direction = "DESC" if current_direction == "ASC" else "ASC"

    # Update the fetch_query to include the ORDER BY clause
    sorted_query = f"{fetch_query} ORDER BY {column} {next_direction}"
    print(f"Sorting {column} in {next_direction} order: {sorted_query}")

    try:
        # Execute the sorted query
        rows = db_manager.execute_query(sorted_query)

        # Clear current data in Treeview
        for item in treeview.get_children():
            treeview.delete(item)

        # Populate Treeview with sorted data
        for row in rows:
            treeview.insert("", "end", values=list(row.values()))

        # Update the sort direction for the column
        sort_directions[column] = next_direction

    except Exception as e:
        messagebox.showerror("Error", f"Failed to sort by {column}: {e}")
        if DEBUG:
            print(f"Error in sort_table: {e}")


def populate_table(treeview, fetch_query): 
    """
    Populates the Treeview with data from the database.
    :param treeview: The Treeview widget.
    :param fetch_query: SQL query to fetch data.
    """
    try:
        # Call db_manager's execute_query directly without passing the connection
        rows = db_manager.execute_query(fetch_query)
       
        # Clear existing rows in the Treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        # Insert rows into the Treeview
        for row in rows:
            treeview.insert("", "end", values=list(row.values()))
       
    except Exception as e:
        messagebox.showerror("Error", f"Failed to populate data: {e}")
        if DEBUG:
            print(f"Error in populate_table: {e}")