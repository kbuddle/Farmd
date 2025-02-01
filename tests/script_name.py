# subject to redistribution within new filing structure.

import sqlite3

DB_PATH = r"D:\FarmbotPythonV2\src\database\farmbot.db"

try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")  # ✅ Enable Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA busy_timeout = 5000;")  # ✅ Set timeout to wait for lock release
    conn.commit()
    conn.close()
    print("✅ SUCCESS: Database settings updated.")
except sqlite3.Error as e:
    print(f"❌ ERROR: {e}")
