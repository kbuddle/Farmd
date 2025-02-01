# Functions to generate SQL queries dynamically.

from src.database.transaction import DatabaseTransactionManager
from tkinter import StringVar

class DatabaseQueryExecutor:
    
    def __init__(self, db_manager: DatabaseTransactionManager):
        self.transaction_manager = db_manager
        self.cursor = self.transaction_manager.cursor

    def execute_query(self, query, params=None, transactional=True):
        try:
            if params:
                if isinstance(params, dict):
                    params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
                elif isinstance(params, (list, tuple)):
                    params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

            if transactional:
                self.transaction_manager.begin_transaction()

            self.cursor.execute(query, params) if params else self.cursor.execute(query)

            if query.strip().lower().startswith("select"):
                return [dict(row) for row in self.cursor.fetchall()]

            if transactional:
                self.transaction_manager.commit_transaction()
                
        except Exception as e:
            if transactional:
                self.transaction_manager.rollback_transaction()
            print(f"Error executing query: {e}")
            raise e

    def execute_non_query(self, query, params=None, transactional=True, commit=False):
        try:
            if params:
                if isinstance(params, dict):
                    params = {k: (v.get() if isinstance(v, StringVar) else v) for k, v in params.items()}
                elif isinstance(params, (list, tuple)):
                    params = tuple((v.get() if isinstance(v, StringVar) else v) for v in params)

            if transactional and not self.transaction_manager.in_transaction:
                self.transaction_manager.begin_transaction()

            self.cursor.execute(query, params) if params else self.cursor.execute(query)

            if commit:
                self.transaction_manager.commit_transaction()
        except Exception as e:
            if transactional:
                self.transaction_manager.rollback_transaction()
            raise e
