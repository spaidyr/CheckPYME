import subprocess
from datetime import datetime
import uuid
import platform

class TemplateTest2():

    def __init__(self):
        
        result = {}
        name = 'TemplateTest2'
        # Agregar código de tiempo y ID único al diccionario
        result = {'id':str(uuid.uuid4())}
        result['module_name'] = name
        result['hostname'] = platform.node()
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_file = self.check(result)

    def check(self, result):

        try:
            pass                            

        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e}")

        return result
