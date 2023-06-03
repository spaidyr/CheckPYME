import subprocess
from datetime import datetime
import uuid
import platform
import re

class PasswordPolicies():

    def __init__(self):
        result = {}
        name = 'PasswordPolicies'
        result = {'id':str(uuid.uuid4())}
        result['module_name'] = name
        result['hostname'] = platform.node()
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_file = self.check(result)

    def check(self, result):

        # Definimos las claves en inglés correspondientes a cada posición
        key_names_eng = [
            'Force logoff after',
            'Min password age (days)',
            'Max password age (days)',
            'Min password length',
            'Length of password history maintained',
            'Lockout threshold',
            'Lockout duration (minutes)',
            'Lockout observation window (minutes)',
            'Computer role'
        ]

        try:
            output = subprocess.run('net accounts', capture_output=True, text=True)
            lines = output.stdout.split('\n')

            data_lines = [line for line in lines if re.search(r':', line)]  # Solo las líneas con datos
            for i, item in enumerate(data_lines):

                # Buscamos el valor usando una expresión regular
                match = re.search(r':\s+(.+)$', item)

                if match:
                    value = match.group(1)
                    key_eng = key_names_eng[i]  # Asignamos la clave en inglés correspondiente a esta posición
                    result[key_eng] = value
                
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")
        return result
