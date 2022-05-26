from enum import Enum
import os
import shutil
import time
import signal
from typing import Callable
from progress.bar import IncrementalBar
import schedule
import logging
import configparser
from logging.handlers import RotatingFileHandler
# 500 MB
max_bytes=500*1024*1024
os.makedirs('logs', exist_ok=True)
file_logger = logging.getLogger('file_logger')
file_logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler('logs/backup_tasker.log', maxBytes=max_bytes, backupCount=10, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
file_logger.addHandler(file_handler)


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

    def __init__(self, source_folders:list[str]=[], destination_folders:list[str]=[], days_to_keep:int=7):
        """
        Initialize the BackupTasker class.
        :param source_folders: The source folders.
        :param destination_folders: The destination folders.
        :param days_to_keep: The number of days to keep the backup files.
        """
        self.source_folders = source_folders
        self.destination_folders = destination_folders
        self.days_to_keep = days_to_keep
        self.time_to_backup = '00:00'
        self.day_to_backup = Weekday.Monday
        self.logger=logging.getLogger('backup_tasker')
    
    @classmethod
    def from_folders(cls, source_folders:list[str], destination_folders:list[str], days_to_keep:int):
        """
        Create a BackupTasker object from the source and destination folders.
        :param source_folders: The source folders.
        :param destination_folders: The destination folders.
        :param days_to_keep: The number of days to keep the backup files.
        :return: The BackupTasker object.
        """
        return cls(source_folders, destination_folders, days_to_keep)

    @classmethod
    def from_config(cls, config_file:str):
        """
        Create a BackupTasker object from a config file.
        :param config_file: The config file.
        :return: The BackupTasker object.
        """
        backup_tasker=BackupTasker()
        backup_tasker.load_config(config_file)
        return backup_tasker

    def load_config(self, config_file:str='config.ini'):
        """
        Load the configuration file.
        :param config_file: The configuration file.
        """
        config=configparser.ConfigParser()
        config.read(config_file)
        # Folders to backup
        source_folders=config['Source Folders to backup']
        # Folders to backup to
        destination_folders=config['Folders to backup']
        # Schedule section
        sched=config['Schedule']

        self.source_folders=source_folders.get('source_path').split(',')
        self.destination_folders=destination_folders.get('backup_path').split(',')
        self.days_to_keep=int(sched.get('days_to_backup'))
        self.time_to_backup=sched.get('time_to_backup')
        self.day_to_backup=Weekday(Weekday[sched.get('day_to_backup')])

    def schedule_backup(self):
        """
        Schedule the backup.
        """
        console_logger=logging.getLogger('console_logger')
        signal.signal(signal.SIGINT, BackupTasker.signal_handler)
        signal.signal(signal.SIGTERM, BackupTasker.signal_handler)
        # Schedule the backup
        backup_job=self.day_to_backup.get_schedule_job().at(self.time_to_backup).do(self.backup)
        try :
            while True:
                wait_time=schedule.idle_seconds()
                if wait_time>0:
                    #Print the time to wait in hours and minutes and seconds and get date of the next scheduled job
                    file_logger.info(f'Waiting {wait_time//3600} hours {wait_time%3600//60} minutes {wait_time%60} seconds until the next scheduled job.')
                    file_logger.info(f'Next scheduled job is {schedule.next_run()}')
                    console_logger.info(f'Waiting {wait_time//3600} hours {wait_time%3600//60} minutes {wait_time%60} seconds until the next scheduled job.')
                    console_logger.info(f'Next scheduled job is {schedule.next_run()}')
                    time.sleep(wait_time)
                schedule.run_pending()
                file_logger.info('Done')
        except KeyboardInterrupt:
            self.logger.error('KeyboardInterrupt received. Exiting.')
            schedule.cancel_job(backup_job)
            self.logger.info('Backup job cancelled.')
            exit(0)
        
    def backup(self):
        """
        Backup the files.
        """
        for source_folder in self.source_folders:
            for destination_folder in self.destination_folders:
                dst_path=os.path.join(destination_folder, os.path.basename(source_folder))
                source_folder=os.path.abspath(source_folder)
                dst_path=os.path.abspath(dst_path)
                file_logger.info(f'Backing up {source_folder} to {dst_path}')
                self.backup_folder(source_folder, dst_path)

    def backup_folder(self, source_folder:str, destination_folder:str, bar:IncrementalBar=None):
        """
        Backup the files in the source folder.
        :param source_folder: The source folder.
        :param destination_folder: The destination folder.
        """
        list_directory=os.listdir(source_folder)
        num_of_files=len(list_directory)
        if num_of_files==0:
            file_logger.info(f'No files to backup in {source_folder}')
            return
        if bar is None:
            bar = IncrementalBar(f'Backing up {source_folder}', suffix='%(percent).1f%% - %(eta)ds', max=num_of_files)
        else:
            bar.index = 0
            bar.max=num_of_files
            bar.update()
        #file_logger.info(f'Backing up {len(list_directory)} files from {source_folder} to {destination_folder}')
        for file in list_directory:
            path=os.path.join(source_folder, file)
            if os.path.isfile(path):
                file_logger.info(f'Backing up {path} to {destination_folder}')
                self.backup_file(path, destination_folder)
            else:
                backup_path=os.path.join(destination_folder, file)
                BackupTasker.util_create_directories(backup_path)
                self.backup_folder(path, backup_path, bar=bar)
            bar.next()
    
    def backup_file(self, source_file:str, destination_folder:str):
        """
        Backup the file.
        :param source_file: The source file.
        :param destination_folder: The destination folder.
        """
        if BackupTasker.util_get_days_since_last_modification(source_file) >= self.days_to_keep:
            destination_file = os.path.join(destination_folder, os.path.basename(source_file))
            BackupTasker.util_create_directories(destination_file)
            shutil.copy(source_file, destination_file)
            file_logger.info(f'Backed up {source_file} to {destination_file}')

    @staticmethod
    def signal_handler(signal, frame):
        """
        Signal handler.
        """
        console_logger = logging.getLogger('console_logger')
        file_logger.info('Signal received. Exiting.')
        console_logger.error('Signal received. Exiting.')
        exit(0)
    @staticmethod
    def util_create_directories(path:str):
        """
        Create the directories.
        :param path: The path.
        """
        dir_path=os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    @staticmethod
    def backup_folder_recursive(source_folder:str, destination_folder:str, days_to_keep:int):
        """
        Backup the files in the source folder recursively.
        :param source_folder: The source folder.
        :param destination_folder: The destination folder.
        """
        list_directory=os.listdir(source_folder)
        if len(list_directory)==0:
            print('No files to backup.')
            return
        p_bar=IncrementalBar(f'Processing ...', max=len(list_directory))
        for file in list_directory:
            path=os.path.join(source_folder, file)
            if os.path.isfile(path):
                BackupTasker.backup_file(path, destination_folder, days_to_keep)
            else:
                backup_path=os.path.join(destination_folder, file)
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                BackupTasker.backup_files(path, backup_path, days_to_keep)
            p_bar.next()
        p_bar.finish()
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
                if BackupTasker.util_get_days_since_last_modification(path) > days:
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


if __name__ == '__main__':
    # Create a logger for console output
    console_logger = logging.getLogger('console_logger')
    console_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    console_logger.addHandler(console_handler)
    console_logger.info('Starting backup tasker')
    tasker=BackupTasker.from_config('backup.ini')

    # Schedule the backup
    tasker.schedule_backup()