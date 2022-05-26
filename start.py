from backup_tasker import BackupTasker

tasker=BackupTasker.from_config('backup.ini')

# Schedule the backup
tasker.schedule_backup()