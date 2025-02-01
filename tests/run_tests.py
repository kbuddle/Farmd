# subject to redistribution within new filing structure.

import unittest
import os
import sys

# Ensure the script runs from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")

    """ print("Discovered tests:", suite)  # ✅ Debugging step
    runner = unittest.TextTestRunner()
    runner.run(suite) """

 
    runner = unittest.TextTestRunner()
    runner.run(suite)
