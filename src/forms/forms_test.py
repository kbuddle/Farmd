# subject to redistribution within new filing structure.

import unittest
import os
from tkinter import Tk
from forms.select_entity import select_image_window  # ✅ Corrected import

class TestSelectImageWindow(unittest.TestCase):
    """Test case for image selection window."""

    def setUp(self):
        """Set up a mock Tkinter root for testing."""
        self.root = Tk()
        self.root.withdraw()  # Hide the main Tk window

        # ✅ Dynamically locate the test folder
        base_dir = os.path.abspath(os.path.dirname(__file__))  
        self.test_folder = os.path.join(base_dir, "MockData", "images")  

        if not os.path.exists(self.test_folder):
            os.makedirs(self.test_folder)  # ✅ Create if missing

    def test_select_image_window_opens(self):
        """Ensure the window opens and displays images from the mock folder."""

        def mock_callback(image_path):
            self.assertTrue(os.path.exists(image_path))  # ✅ Ensure valid selection

        window = select_image_window(self.root, self.test_folder, mock_callback)
        self.assertIsNotNone(window)

    def tearDown(self):
        """Clean up by destroying Tk root."""
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()
