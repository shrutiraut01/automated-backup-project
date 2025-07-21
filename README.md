# Automated Backup and Rotation Script with Google Drive Integration

This project provides a robust and automated backup solution that supports scheduled backups, daily/weekly/monthly rotation, Google Drive integration via `rclone`, and notification via webhook. It's ideal for developers and teams who need to regularly back up a GitHub-hosted project or directory with automatic cloud uploads and log tracking.

---

## 📁 Project Structure

auto-backup-project/
├── backup.py # Main backup script (Python)
├── config.env # Environment variables (Google Drive path, webhook URL, etc.)
├── backup.sh # Shell script to call Python script and load config
├── cron_jobs.txt # Crontab entries for scheduling
├── logs/ # Backup log files
└── backups/ # Generated backups (structured by date)

---

## ✅ Features

- 🔁 **Automatic Daily/Weekly/Monthly Backup Rotation**
- ☁️ **Google Drive Upload** using `rclone`
- 📦 **Zips the Project Directory**
- 📜 **Log File Generation**
- 🚨 **Webhook Notification Support**
- 📅 **Cron-Based Scheduling**
- 🔐 **Environment-Based Configuration**

---

## ⚙️ Prerequisites

- Python 3.x
- rclone configured with your Google Drive account
- `zip`, `cron`, and basic Linux utilities
- Webhook URL (optional)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auto-backup-project.git
cd auto-backup-project
2. Configure Environment
Create a .env file or modify config.env:


# config.env
PROJECT_NAME=MyProject
SOURCE_DIR=/path/to/project
BACKUP_DIR=./backups
LOG_DIR=./logs
RCLONE_REMOTE=gdrive:MyBackups
WEBHOOK_URL=https://your-webhook.site/...
RETENTION_DAYS=7
RETENTION_WEEKS=4
RETENTION_MONTHS=6
✅ Make sure rclone is already configured with gdrive remote using rclone config.

3. Run Manually (Optional)

bash backup.sh
4. Set Up Cron Jobs
To schedule automatic daily, weekly, and monthly backups:


crontab cron_jobs.txt
Example entries in cron_jobs.txt:

0 2 * * * /bin/bash /path/to/auto-backup-project/backup.sh daily
0 3 * * 0 /bin/bash /path/to/auto-backup-project/backup.sh weekly
0 4 1 * * /bin/bash /path/to/auto-backup-project/backup.sh monthly
🔄 Rotation Policy
Daily: Keep last 7 backups

Weekly: Keep last 4 backups

Monthly: Keep last 6 backups

Older files are automatically deleted to save space

📤 Google Drive Upload
Uses rclone to upload zipped backups to your Google Drive.

Ensure the target folder (MyBackups) exists in your drive or will be auto-created.

Upload logs are saved with timestamps.

🚨 Webhook Integration
Notifies your custom endpoint (like Slack, Discord, etc.) after each backup.

Sends JSON payload with status and filename.

📄 Logs
Logs are created in the logs/ folder for each backup attempt.

Sample log output:

[2025-07-15 18:29:33] Created backup: MyProject_20250715_182933.zip
[2025-07-15 18:29:36] Uploaded to Google Drive: MyProject_20250715_182933.zip
[2025-07-15 18:29:37] Notification sent to webhook
