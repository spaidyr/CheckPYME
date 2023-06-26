from datetime import datetime
import platform
import pytz
import configparser

SECPOL_PATH = "C:\\TEMP\\secpol.inf"

class UserRightsPolicies():

    def __init__(self) -> dict:

        self.result = {}
        name = 'UserRightsPolicies'
        self.result['module_name'] = name
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = self.check()

    def check(self):

        try:
            policy_values = self.__read_secpol()
            for key, value in policy_values.items():
                self.result[key] = value
        except:
            pass
        return self.result

    def __read_secpol(self):
        secpol = configparser.ConfigParser()
        secpol.optionxform = str  # Conservar la capitalización de las claves
        
        with open(SECPOL_PATH, 'rb') as f:
            content = f.read().decode('utf-16')

        secpol.read_string(content)

        section = 'Privilege Rights'
        keys = ['SeSecurityPrivilege',
                'SeIncreaseQuotaPrivilege',
                'SeShutdownPrivilege',
                'SeIncreaseWorkingSetPrivilege',
                'SeIncreaseBasePriorityPrivilege',
                'SeSystemtimePrivilege',
                'SeTimeZonePrivilege',
                'SeLoadDriverPrivilege',
                'SeCreateGlobalPrivilege',
                'SeCreatePagefilePrivilege',
                'SeCreateSymbolicLinkPrivilege',
                'SeDenyNetworkLogonRight',
                'SeDenyInteractiveLogonRight',
                'SeDebugPrivilege',
                'SeRemoteShutdownPrivilege',
                'SeAuditPrivilege',
                'SeBackupPrivilege',
                'SeSystemEnvironmentPrivilege',
                'SeDelegateSessionUserImpersonatePrivilege',
                'SeChangeNotifyPrivilege',
                'SeInteractiveLogonRight',
                'SeUndockPrivilege',
                'SeManageVolumePrivilege',
                'SeAssignPrimaryTokenPrivilege',
                'SeRestorePrivilege',
                'SeImpersonatePrivilege',
                'SeNetworkLogonRight',
                'SeTakeOwnershipPrivilege',
                'SeBatchLogonRight',
                'SeServiceLogonRight',
                'SeRemoteInteractiveLogonRight']
        
        values = {}
        if secpol.has_section(section):
            for key in keys:
                if secpol.has_option(section, key):
                    values[key] = secpol.get(section, key)
        return values
        
