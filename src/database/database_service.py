import sqlite3
import logging
import tkinter as tk
import tkinter as messagebox    


from config.config_data import DATABASE_PATH, COLUMN_DEFINITIONS
from src.database.database_manager import DatabaseManager
from src.database.query_generator import QueryGenerator
from src.services.validation_service import ValidationService



logger = logging.getLogger(__name__)
dp_path = DATABASE_PATH

class DatabaseService:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_manager = DatabaseManager(db_path)
    
        self.validation_service = ValidationService(COLUMN_DEFINITIONS, self)
        
    def add_item(self, entity_name, form_data):
        """ Inserts a new record into the database, handling validation and constraints. """
            
        if not form_data:
            messagebox.showerror("Error", "No data provided for new item.")
            return

        try:
            # ✅ Validate form data before attempting insert
            self.validation_service.validate_form_data(entity_name, form_data, is_new_entry=True)

            # ✅ Remove primary key for insert (handled by the database)
            primary_key_column = self.get_primary_key(entity_name)
            if primary_key_column in form_data:
                del form_data[primary_key_column]  # ✅ Remove auto-increment primary key

            print(f"🔍 Insert Attempt: {form_data}")  # ✅ Debugging Output

            # ✅ Generate SQL query for INSERT
            query_generator = QueryGenerator(entity_name, primary_key_column)
            insert_query, params = query_generator.generate_insert_query(form_data)

            # ✅ Execute the insert operation using db_manager
            self.db_manager.execute_query(insert_query, params)

            print(f"✅ New {entity_name} record added.")

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))  # ✅ Show validation message
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Database constraint failed: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An unexpected database error occurred: {e}")

    def update_item(self, context, data):
        """ Updates an entity record in the database. The primary key is used to identify the record but is not updated. """
        query_generator = QueryGenerator(context, self.get_primary_key(context))

        # ✅ Get the primary key column
        primary_key_column = self.get_primary_key(context)

        # ✅ Extract the primary key value from `data`
        if primary_key_column not in data:
            raise ValueError(f"❌ Missing primary key '{primary_key_column}' in data for update.")

        primary_key_value = data.pop(primary_key_column)  # ✅ Remove primary key from `data`
        
        # ✅ Generate SQL query
        update_query, params = query_generator.generate_update_query(data)

        # ✅ Append primary key to `params` for WHERE clause
        params.append(primary_key_value)

        return self.db_manager.execute_query(update_query, params)

    def delete_item(self, context, item_id):
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        delete_query, params = query_generator.generate_delete_query()
        return self.db_manager.execute_query(delete_query, (item_id,))

    def fetch_all(self, context, item_id=None):
        """Fetch all records from a given table. If `item_id` is provided, fetch only that record."""
        query_generator = QueryGenerator(context, self.get_primary_key(context))
        fetch_query = query_generator.generate_fetch_query()

        params = ()
        if item_id:
            fetch_query += f" WHERE {self.get_primary_key(context)} = ?"
            params = (item_id,)

        print(f"🔍 Running Query: {fetch_query} with params {params}")  # ✅ Debugging output

        results = self.db_manager.execute_query(fetch_query, params)

        if not results:
            print(f"⚠️ No results found for {context}. Returning empty list.")
            return []

        corrected_results = []
        for row in results:
            #print(f"🛠️ Mapping row: {dict(row)}")  # ✅ Debugging output
            corrected_results.append(dict(row))

        #print(f"✅ Corrected Mapped Results: {corrected_results}")  # ✅ Debugging output

        return corrected_results
            
    def get_primary_key(self, context):
        """Retrieves the primary key column for a given table context."""
        column_definitions = COLUMN_DEFINITIONS.get(context, {}).get("columns", {})

        if not column_definitions:
            print(f"❌ No column definitions found for {context}. Check config.")
            return None  # ✅ Return None if column definitions are missing
        
        primary_key = next(
            (col for col, details in column_definitions.items() if details.get("is_primary_key", False)), 
            None
        )

        if not primary_key:
            print(f"❌ No primary key defined for context: {context}")
            return None  # ✅ Return None if no primary key exists

        print(f"✅ Found Primary Key for {context}: {primary_key}")  # ✅ Debugging output
        return primary_key
    
    def fetch_one(self, query, params=()):
        """Fetch a single row from the database."""
        try:
            cursor = self.db_manager.connection.cursor()  # ✅ Corrected typo and assigned cursor
            cursor.execute(query, params)
            result = cursor.fetchone()  # ✅ Fetches the first row or None
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        
    def fetch_raw(self, query, params=()):
        """Fetch all rows using a raw SQL query and return them as tuples."""
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()  # ✅ Fetch raw sqlite3.Row objects

            # ✅ Convert sqlite3.Row objects to standard tuples (ImageID, ImageFilename)
            formatted_results = [tuple(row) for row in results]

            return formatted_results
        except sqlite3.Error as e:
            print(f"❌ Database error in fetch_raw: {e}")
            return []

    def execute_query(self, query, params=()):
        return self.db_manager.execute_query(query, params)