from src.database.queries import DatabaseQueryExecutor
from src.database.transaction import DatabaseTransactionManager

class TableManager:
    """
    Manages the Treeview table, handling sorting and database population.
    """

    def __init__(self, db_manager):
        """
        Initializes the TableManager with a database transaction manager.

        Args:
            db_manager (DatabaseTransactionManager): Handles database interactions.
        """
        self.db_manager = db_manager
        self.db_query_executor = DatabaseQueryExecutor(db_manager)  # ✅ Correct way to instantiate DatabaseQueryExecutor
        self.sort_directions = {}  # Tracks sorting direction for each column

    def create_treeview(self, parent, columns):
        """
        Creates a Treeview widget inside the given parent frame.

        Args:
            parent (Frame): The parent container for the Treeview.
            columns (list): List of column names to display.

        Returns:
            ttk.Treeview: Configured Treeview widget.
        """
        treeview = ttk.Treeview(parent, columns=columns, show="headings")

        # Configure column headers
        for col in columns:
            treeview.heading(col, text=col, command=lambda c=col: self.sort_table(treeview, c, False))
            treeview.column(col, width=100, anchor="w")  # Set default width

        treeview.pack(fill="both", expand=True)
        return treeview

    def sort_table(self, treeview, column, reverse):
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
            treeview.heading(column, command=lambda: self.sort_table(treeview, column, not reverse))

        except Exception as e:
            print(f"ERROR: Sorting failed for column {column}. {e}")

    def populate_table(self, treeview, fetch_query, params=None, debug=True): 
        """
        Populates the Treeview with data from the database.

        Args:
            treeview (ttk.Treeview): The Treeview to populate.
            fetch_query (str): SQL query to fetch data.
            params (tuple, optional): Query parameters. Defaults to None.
            debug (bool, optional): Prints debug information. Defaults to True.
        """
        if debug:
            print(f"🔍 DEBUG: Fetch Query = {fetch_query}, Params = {params}")

        try:
            # Fetch results from database
            rows = self.db_query_executor.execute_query(fetch_query, params=params, debug=debug)

            # Print fetched rows for debugging
            print(f"✅ DEBUG: Query returned {len(rows)} rows")

            # Clear existing rows in the Treeview
            for item in treeview.get_children():
                treeview.delete(item)
            
            # Insert rows into the Treeview
            for row in rows:
                treeview.insert("", "end", values=list(row.values()))

        except Exception as e:
            print(f"❌ ERROR in populate_table: {e}")
