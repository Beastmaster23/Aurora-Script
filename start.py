import logging
from backup_tasker import BackupTasker

tasker=BackupTasker.from_config('backup.ini')
# Create a logger for console output
console_logger = logging.getLogger('console_logger')
console_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
console_logger.addHandler(console_handler)
console_logger.info('Starting backup tasker')
# Schedule the backup
tasker.schedule_backup()