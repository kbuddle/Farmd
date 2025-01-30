import unittest
from core.database_queries import fetch_available_items

class TestFetchAvailableItems(unittest.TestCase):
    """Unit test for fetch_available_items function."""

    def test_fetch_available_items(self):
        """Tests that the function returns correct available items."""
        assembly_id = 1  # Replace with a valid assembly ID from test data
        available_items = fetch_available_items(assembly_id)

        print(fetch_available_items(1))
        
        self.assertIsInstance(available_items, list)
        if available_items:
            self.assertIn("ID", available_items[0])
            self.assertIn("Name", available_items[0])
            self.assertIn("EntityType", available_items[0])

if __name__ == "__main__":
    unittest.main()
