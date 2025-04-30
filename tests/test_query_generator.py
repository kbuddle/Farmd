import unittest
from src.database.query_generator import QueryGenerator

class TestQueryGenerator(unittest.TestCase):

    def setUp(self):
        """Setup QueryGenerator for testing"""
        self.query_gen = QueryGenerator(context_name="Assemblies", debug=False)

    def test_fetch_query(self):
        """Test if fetch query is generated correctly"""
        query = self.query_gen.generate_fetch_query()
        self.assertIn("SELECT", query)
        self.assertIn("FROM Assemblies", query)

    def test_insert_query(self):
        """Test if insert query is generated correctly"""
        query = self.query_gen.generate_insert_query()
        self.assertIn("INSERT INTO Assemblies", query)

    def test_update_query(self):
        """Test if update query is generated correctly"""
        query = self.query_gen.generate_update_query()
        self.assertIn("UPDATE Assemblies", query)

    def test_delete_query(self):
        """Test if delete query is generated correctly"""
        query = self.query_gen.generate_delete_query()
        self.assertIn("DELETE FROM Assemblies", query)

if __name__ == "__main__":
    unittest.main()

