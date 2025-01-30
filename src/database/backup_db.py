import os
import shutil
from datetime import datetime

# Define paths
DB_FILE = "src/db/app_data.sqlite"
BACKUP_FOLDER = "src/db/backups/"

# Ensure the backup folder exists
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def backup_database():
    """Creates a timestamped backup of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.sqlite"
    backup_path = os.path.join(BACKUP_FOLDER, backup_filename)

    try:
        shutil.copy2(DB_FILE, backup_path)
        print(f"✅ Database backup successful: {backup_path}")
    except Exception as e:
        print(f"🚨 Backup failed: {e}")

if __name__ == "__main__":
    backup_database()
