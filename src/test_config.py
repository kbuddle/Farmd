import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config_data import DATABASE_PATH

print(f"✅ DATABASE_PATH: {DATABASE_PATH}")
print(f"📂 Does the database exist? {os.path.exists(DATABASE_PATH)}")
