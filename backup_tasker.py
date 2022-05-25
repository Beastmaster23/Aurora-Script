from enum import Enum
import os
import shutil
import time
from typing import Callable
from progress.bar import IncrementalBar
import schedule

class Weekday(Enum):
    """
    Enum for weekdays.
    """
    Monday=0
    Tuesday=1
    Wednesday=2
    Thursday=3
    Friday=4
    Saturday=5
    Sunday=6

    def get_schedule_job(self) -> None:
        """
        Schedule a job for the weekday.
        """
        schedule_job = None
        match self.value:
            case 0:
                schedule_job=schedule.every().monday
            case 1:
                schedule_job=schedule.every().tuesday
            case 2:
                schedule_job=schedule.every().wednesday
            case 3:
                schedule_job=schedule.every().thursday
            case 4:
                schedule_job=schedule.every().friday
            case 5:
                schedule_job=schedule.every().saturday
            case 6:
                schedule_job=schedule.every().sunday
        return schedule_job

class BackupTasker:
    """
    BackupTasker class is used to backup a file or directory.
    """

    def __init__(self, source_folders:list[str], destination_folders:list[str], days_to_keep:int):
        """
        Initialize the BackupTasker class.
        :param source_folders: The source folders.
        :param destination_folders: The destination folders.
        :param days_to_keep: The number of days to keep the backup files.
        """
        self.source_folders = source_folders
        self.destination_folders = destination_folders
        self.days_to_keep = days_to_keep
    
    def backup(self):
        """
        Backup the files.
        """
        for source_folder in self.source_folders:
            for destination_folder in self.destination_folders:
                self.backup_folder(source_folder, destination_folder)

    def backup_folder(self, source_folder:str, destination_folder:str):
        """
        Backup the files in the source folder.
        :param source_folder: The source folder.
        :param destination_folder: The destination folder.
        """
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                self.backup_file(os.path.join(root, file), destination_folder)
    
    def backup_file(self, source_file:str, destination_folder:str):
        """
        Backup the file.
        :param source_file: The source file.
        :param destination_folder: The destination folder.
        """
        if BackupTasker.util_get_days_since_last_modification(source_file) > self.days_to_keep:
            destination_file = os.path.join(destination_folder, os.path.basename(source_file))
            if not os.path.exists(destination_file):
                os.makedirs(destination_file)
            shutil.copy(source_file, destination_file)
    
    @staticmethod
    def backup_files(dir:str, backup_dir:str, days:int):
        """
        Backup files in a directory.
        :param dir: The directory to backup.
        :param backup_dir: The backup directory.
        :param days: The number of days to keep the backup files.
        """
        list_directory=os.listdir(dir)
        if len(list_directory)==0:
            print('No files to backup.')
            return
        p_bar=IncrementalBar(f'Processing ...', max=len(list_directory))
        for file in list_directory:
            path=os.path.join(dir, file)
            if os.path.isfile(path):
                if BackupTasker.get_days_since_last_modification(path) > days:
                    backup_path=os.path.join(backup_dir, file)
                    if not os.path.exists(backup_path):
                        os.makedirs(backup_path)
                    shutil.copy(path, backup_path)
            else:
                backup_path=os.path.join(backup_dir, file)
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                BackupTasker.backup_files(path, backup_path, days)
            p_bar.next()
        p_bar.finish()
    @staticmethod
    def compare_files(src:str, dst:str, callback:Callable):
        """
        Compare files if they exist in the src with the files that exist in the dst.
        :param src: The directory to compare from.
        :param dst: The directory to compare to.
        """
        files=[]
        # Loop through the files in the directory
        for file in os.listdir(src):
            path1=os.path.join(src, file)
            if os.path.isfile(path1):
                path2=os.path.join(dst, file)
                if not os.path.isfile(path2):
                    files.append(file)
                    callback(file)
        return files
    @staticmethod
    def util_get_days_since_last_modification(path:str) -> int:
        """
        Get the number of days since the last modification.
        :param path: The file path.
        :return: The number of days since the last modification.
        """
        return (time.time() - os.path.getmtime(path)) // (24 * 60 * 60)
    @staticmethod
    def util_remove_same(src:list, dst:list):
        """
        Return the files that are not in the dst.
        :param src: The source list.
        :param dst: The destination list.
        """
        temp=[]
        for item in src:
            if not item in dst:
                temp.append(item)
        return temp