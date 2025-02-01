# subject to redistribution within new filing structure.

import unittest
import os
from tkinter import Tk
from forms.select_entity import select_image_window  # ✅ Import function instead of defining it

class TestSelectImageWindow(unittest.TestCase):
    """Test case for image selection window."""

    def setUp(self):
        """Set up a mock Tkinter root for testing."""
        self.root = Tk()
        self.root.withdraw()  # Hide the main Tk window

        # ✅ Use the correct folder path
        self.test_folder = r"D:\FarmbotPythonV2\tests\MockData\images"

        if not os.path.exists(self.test_folder):
            os.makedirs(self.test_folder)  # ✅ Ensure test folder exists

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
