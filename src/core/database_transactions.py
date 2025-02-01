# subject to redistribution within new filing structure.


import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk, Frame  # Consolidated imports
from config.config_data import DEBUG, COLUMN_DEFINITIONS, DATABASE_PATH

db_path = DATABASE_PATH
debug = False,



class ConnectionTracker:
    
    def __init__(self):
        self.open_connections = []

    def add_connection(self, connection):
        #print("DEBUG: add_connection called")  # Add debug
        debug=False
        self.open_connections.append(connection)
        if debug:
            print(f"DEBUG: Connection opened. Total connections: {len(self.open_connections)}")

    def remove_connection(self, connection):
        #print("DEBUG: remove_connection called")  # Add debug
        debug=False
        if connection in self.open_connections:
            self.open_connections.remove(connection)
            if debug:
                print(f"DEBUG: Connection closed. Total connections: {len(self.open_connections)}")
        else:
            if debug:
                print(f"DEBUG: Attempted to close a connection that was not tracked.")

    def force_close_all(self):
        """ Force close all connections to avoid leaks """
        debug=False
        for conn in self.open_connections.copy():
            if debug:
                print(f"DEBUG: Force closing lingering connection {conn}")
            conn.close()
            self.remove_connection(conn)

class DatabaseTransactionManager:
    _instance = None  # Singleton instance
    connection_tracker = ConnectionTracker()
    
    def __new__(cls, db_path):
        if cls._instance is None:
            cls._instance = super(DatabaseTransactionManager, cls).__new__(cls)
            cls._instance._init(db_path)
        return cls._instance

    def _init(self, db_path):
        """ Initialize database connection only once """
        self.connection = sqlite3.connect(db_path, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.in_transaction = False
        self.connection_tracker.add_connection(self.connection)
        
    def close(self):
        """ Close the database connection and reset the singleton """
        self.cursor.close()
        self.connection.close()
        self.connection_tracker.remove_connection(self.connection)
        DatabaseTransactionManager._instance = None

    def begin_transaction(self, debug=False):
        debug=False
        if debug:
            print(f"DEBUG: Checking if transaction is active: {self.in_transaction}")  # Debugging
        """
        Start a transaction for the current operation.
        """
        if not self.in_transaction:
            self.connection.execute("BEGIN TRANSACTION;")
            self.in_transaction = True
            if debug:
                print("DEBUG: Transaction started inside begin_transaction()")  # Debugging

    def commit_transaction(self, debug=DEBUG):
        """
        Commit the current transaction and finalize the changes.
        """
        debug=False
        if self.in_transaction:
            self.connection.commit()
            self.in_transaction = False
            if debug:
                print("DEBUG: Transaction committed.")

    def execute_query(self, query, params=None, transactional=True, debug=DEBUG):
        """
        Execute a query on the SQLite database and return results as dictionaries.
        """
        try:
            if debug:
                print(f"DEBUG EXECUTE: Query type: {type(query)}, Query: {query}")
                print(f"DEBUG EXECUTE: Params: {params}")# Preprocess params to handle StringVar objects
            if params:
                if isinstance(params, dict):
                    params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
                elif isinstance(params, (list, tuple)):
                    params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

            # Start transaction if needed
            if transactional:
                self.begin_transaction()
                if debug:
                    print("DEBUG: Transaction started.")

            # Execute the query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            # Fetch results for SELECT queries
            if query.strip().lower().startswith("select"):
                return [dict(row) for row in self.cursor.fetchall()]

            # Commit the transaction if transactional
            if transactional:
                self.commit_transaction()
                if debug:
                    print("DEBUG: Transaction committed.")

        except Exception as e:
            # Rollback transaction on error
            if transactional:
                self.rollback_transaction()
                if debug:
                    print("DEBUG: Transaction rolled back due to error.")
            print(f"Unexpected error: {e}")
            raise e
        finally:
            if debug:
                print(f"DEBUG: Closing connection in execute_query")
            #self.close()  # Ensure connection is closed

    def execute_non_query(self, query, params=None, transactional=True, commit=False, debug=False):
        """
        Execute a non-query SQL statement (e.g., INSERT, UPDATE, DELETE).
        """
        try:
            if debug:
                print(f"DEBUG EXECUTE_NON_QUERY: Query type: {type(query)}, Query: {query}")
                print(f"DEBUG EXECUTE_NON_QUERY: Params: {params}")# Preprocess params to handle StringVar objects
            # Preprocess params to handle StringVar objects
            if params:
                if isinstance(params, dict):
                    params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
                elif isinstance(params, (list, tuple)):
                    params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

            # Start transaction if needed
            if transactional and not self.in_transaction:
                self.begin_transaction()
                if debug:
                    print("DEBUG EXECUTE NON: Transaction started.")

            # Execute the query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            # Explicitly commit if requested
            if commit:
                self.commit_transaction()
                if debug:
                    print("DEBUG: Transaction committed after non-query execution.")
            else:
                if debug:
                    print("DEBUG: Transaction left open for potential rollback.")     
                    
        except Exception as e:
            # Rollback transaction on error
            if transactional:
                self.rollback_transaction()
                if debug:
                    print(f"DEBUG: Transaction rolled back due to error. Unexpected error: {e} ")
            raise e

    def rollback_transaction(self, debug=False):
        """
        Rollback the current transaction, undoing all changes made since it started.
        """
        if self.in_transaction:
            if debug:
                 print("DEBUG: Rolling back transaction...")
            self.connection.rollback()
            self.in_transaction = False
            if debug:
                print("DEBUG: Transaction rollback succesfull.")
            else:
                print("DEBUG: No active transaction to rollback")

def undo_last_action(table, fetch_query, debug=False):
    """
    Undo the last database transaction by rolling it back and refreshing the table.
    """
    try:
        if not db_manager.in_transaction:
            print("DEBUG: No active transaction to rollback.")
            messagebox.showerror("Undo Failed", "No active transaction to rollback.")
            return

        print("DEBUG: Attempting rollback...")
        db_manager.rollback_transaction()

        # Fetch updated data from the database
        print("DEBUG: Fetching data after rollback...")
        rows = db_manager.execute_query(fetch_query)

        if rows:
            print(f"DEBUG: Data after rollback: {rows}")
        else:
            print("DEBUG: No changes detected after rollback.")

        # Clear and repopulate the table
        table.delete(*table.get_children())
        for row in rows:
            table.insert("", "end", values=tuple(row.values()))

        messagebox.showinfo("Undo", "Last action has been undone successfully.")

    except Exception as e:
        print(f"DEBUG: Undo failed: {e}")
        messagebox.showerror("Undo Failed", f"Could not undo the last action: {e}")

db_manager= DatabaseTransactionManager(DATABASE_PATH)
