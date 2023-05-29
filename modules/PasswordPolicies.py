import subprocess
from datetime import datetime
import uuid
import platform
import re

class PasswordPolicies():

    def __init__(self):
        result = {}
        name = 'PasswordPolicies'
         # Agregar código de tiempo y ID único al diccionario
        result = {'id':str(uuid.uuid4())}
        result['module_name'] = name
        result['hostname'] = platform.node()
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
