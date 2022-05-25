from enum import Enum
import os
import shutil
from typing import Callable
from progress.bar import IncrementalBar
import schedule
import time
import configparser
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
def remove_same(src:list, dst:list):
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
            if get_days_since_last_modification(path) > days:
                backup_path=os.path.join(backup_dir, file)
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                shutil.copy(path, backup_path)
        else:
            backup_path=os.path.join(backup_dir, file)
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            backup_files(path, backup_path, days)
        p_bar.next()
    p_bar.finish()

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


    print(f'Copied {num_of_files} files.')

def get_days_since_last_modification(path:str) -> int:
    """
    Get the number of days since the last modification.
    :param path: The file path.
    :return: The number of days since the last modification.
    """
    return (time.time() - os.path.getmtime(path)) // (24 * 60 * 60)

# Don't run the script folders are in the same directory or nested in the same directory
file_path='C:\\Users\\edn12\\Downloads\\'
backup_path='C:\\Users\\edn12\\backup'
days_to_backup=0
time_to_backup="14:43"#1:30 pm
day_to_backup=Weekday.Wednesday

config=configparser.ConfigParser()
config.read('backup.ini')
# Folders to backup
source_folders=config['Source Folders to backup']
# Folders to backup to
destination_folders=config['Folders to backup']
# Schedule section
sched=config['Schedule']
file_path=source_folders.get('source_path')
backup_path=destination_folders.get('backup_path')
#print(f'Source path: {file_path} and backup path: {backup_path}')

day_to_backup= Weekday[sched.get('day_to_backup')]
time_to_backup=sched.get('time_to_backup')
days_to_backup=int(sched.getfloat('days_to_backup'))

# Schedule the backup
backup_job=day_to_backup.get_schedule_job().at(time_to_backup).do(backup_files, file_path, backup_path, days_to_backup)
try :
    while True:
        wait_time=schedule.idle_seconds()
        if wait_time>0:
            #Print the time to wait in hours and minutes and seconds and get date of the next scheduled job
            print(f'Waiting {wait_time//3600} hours {wait_time%3600//60} minutes {wait_time%60} seconds until the next scheduled job.')
            print(f'Next scheduled job is {schedule.next_run()}')
            time.sleep(wait_time)
        schedule.run_pending()
except KeyboardInterrupt:
    print('Stopping ...')
    schedule.cancel_job(backup_job)
    print('Done.')