import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from backup_tasker import BackupTasker

#Create a windows service to run the backup tasker
#This will run the backup tasker in the background

class BackupService(win32serviceutil.ServiceFramework):
    _svc_name_ = "BackupService"
    _svc_display_name_ = "Backup Service"
    _svc_description_ = "This service will run the backup tasker in the background"

    def __init__(self, args):
        self.please_stop = False
        self.backup_tasker = BackupTasker.from_config('backup.ini')
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.backup_tasker.stop_backup()
    
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        self.main()

    def main(self):
        self.backup_tasker.schedule_backup()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BackupService)