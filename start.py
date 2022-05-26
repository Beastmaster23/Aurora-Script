from enum import Enum
import os
import shutil
from typing import Callable
from progress.bar import IncrementalBar
import schedule
import time
import configparser
from backup_tasker import BackupTasker, Weekday

tasker=BackupTasker(["C:\\Users\\edn12\\Downloads", "C:\\Users\\edn12\\Desktop"], ["C:\\Users\\edn12\\backup"], 0)
tasker.load_config()
# Schedule the backup
tasker.schedule_backup()