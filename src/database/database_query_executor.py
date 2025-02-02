# Functions to generate SQL queries dynamically.
import sqlite3

from src.database.database_transaction import DatabaseTransactionManager
from tkinter import StringVar
import logging

logger = logging.getLogger(__name__)

class DatabaseQueryExecutor:
    
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.connection = self.database_manager.get_connection() 
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None, commit=True):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            if commit:
                self.connection.commit()

            return self.cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Database query failed: {e}")

    def execute_non_query(self, query, params=None, transactional=True, commit=False):
        try:
            if params:
                if isinstance(params, dict):
                    params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
                elif isinstance(params, (list, tuple)):
                    params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

            if transactional and not self.database_manager.in_transaction:
                self.database_manager.begin_transaction()

            self.cursor.execute(query, params) if params else self.cursor.execute(query)

            if commit:
                self.database_manager.commit_transaction()
        except Exception as e:
            if transactional:
                self.database_manager.rollback_transaction()
            raise e
