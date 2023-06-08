import subprocess
from datetime import datetime
import platform
import re
import pytz

class PasswordPolicies():

    def __init__(self):
        result = {}
        name = 'PasswordPolicies'
        result['module_name'] = name
        result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = self.check(result)

    def check(self, result):

        try:
            output = subprocess.run('net accounts', capture_output=True, text=True)
            lines = output.stdout.split('\n')

            for item in lines:
                # Buscamos la clave y el valor usando expresiones regulares
                match = re.search(r'^(.+):\s+(.+)$', item)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    result[key] = value
                
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")

        return result
