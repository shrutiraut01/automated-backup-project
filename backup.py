import os
import zipfile
import datetime
import shutil
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
import subprocess

# Load environment variables
load_dotenv()

# Environment variables
PROJECT_NAME = os.getenv("PROJECT_NAME")
PROJECT_DIR = os.getenv("PROJECT_DIR")
BACKUP_DIR = os.getenv("BACKUP_DIR")
RCLONE_REMOTE = os.getenv("RCLONE_REMOTE")
RCLONE_FOLDER = os.getenv("RCLONE_FOLDER")
LOG_FILE = os.getenv("LOG_FILE", "backup.log")
NOTIFY_URL = os.getenv("NOTIFY_URL")
ENABLE_NOTIFY = os.getenv("ENABLE_NOTIFY", "true").lower() == "true"

RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 7))
RETENTION_WEEKS = int(os.getenv("RETENTION_WEEKS", 4))
RETENTION_MONTHS = int(os.getenv("RETENTION_MONTHS", 3))


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def create_backup():
    now = datetime.datetime.now()
    date_path = now.strftime("%Y/%m/%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    zip_name = f"{PROJECT_NAME}_{timestamp}.zip"

    backup_path = os.path.join(BACKUP_DIR, PROJECT_NAME, date_path)
    os.makedirs(backup_path, exist_ok=True)
    zip_path = os.path.join(backup_path, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PROJECT_DIR)
                zipf.write(file_path, arcname)

    log(f"Created backup: {zip_path}")
    return zip_path


def upload_to_drive(zip_path):
    try:
        result = subprocess.run([
            "rclone", "copy", zip_path, f"{RCLONE_REMOTE}:{RCLONE_FOLDER}"
        ], check=True, capture_output=True, text=True)
        log(f"Uploaded to Google Drive: {Path(zip_path).name}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Upload failed: {e.stderr}")
        return False


def send_notification(zip_path):
    if not ENABLE_NOTIFY:
        return

    payload = {
        "project": PROJECT_NAME,
        "date": datetime.datetime.now().isoformat(),
        "status": "BackupSuccessful",
        "file": os.path.basename(zip_path)
    }

    try:
        response = requests.post(NOTIFY_URL, json=payload, timeout=10)
        response.raise_for_status()
        log("Webhook notification sent.")
    except Exception as e:
        log(f"Webhook failed: {str(e)}")


def rotate_backups():
    root_path = Path(BACKUP_DIR) / PROJECT_NAME
    now = datetime.datetime.now()
    deleted = []

    if not root_path.exists():
        return

    for year_dir in root_path.iterdir():
        if not year_dir.is_dir(): continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir(): continue
            for day_dir in month_dir.iterdir():
                if not day_dir.is_dir(): continue

                day = datetime.datetime.strptime(
                    f"{year_dir.name}-{month_dir.name}-{day_dir.name}", "%Y-%m-%d"
                )

                age_days = (now - day).days
                weekday = day.weekday()  # Monday = 0, Sunday = 6

                if (
                    age_days > RETENTION_DAYS and
                    (weekday != 6 or age_days > RETENTION_WEEKS * 7) and
                    (day.day != 1 or age_days > RETENTION_MONTHS * 30)
                ):
                    shutil.rmtree(day_dir)
                    deleted.append(str(day_dir))

    if deleted:
        log(f"Deleted {len(deleted)} old backups.")
    else:
        log("No old backups deleted.")


def main():
    zip_path = create_backup()
    if upload_to_drive(zip_path):
        send_notification(zip_path)
    rotate_backups()
    log("Backup process completed.\n")


if __name__ == "__main__":
    main()
