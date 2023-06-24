import subprocess
from datetime import datetime
import platform
import re
import pytz

class AccountsPolicies():

    def __init__(self) -> dict:
        self.result = {}
        name = 'AccountsPolicies'
        self.result['module_name'] = name
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = self.check()

    def check(self):

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
        
        # Definimos las claves que queremos mantener
        keys_to_keep = [
            'Lockout threshold',
            'Lockout duration (minutes)',
            'Lockout observation window (minutes)'
        ]

        # Definimos las claves que queremos convertir a entero
        keys_to_int = [
            'Lockout duration (minutes)',
            'Lockout observation window (minutes)'
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
                    
                    # Solo almacenamos en el diccionario si la clave está en keys_to_keep
                    if key_eng in keys_to_keep:
                        # Convertimos a entero si la clave está en keys_to_int
                        if key_eng in keys_to_int:
                            value = int(value)
                        self.result[key_eng] = value
                
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")

        return self.result
