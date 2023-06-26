import subprocess
import os
from datetime import datetime
import platform
import pytz

class AASecedit():

    def __init__(self) -> dict:
        self.result = {}
        name = 'AASecedit'
        self.result['module_name'] = name
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = self.check()

    def check(self):
        
        self.run_powershell_command()        

    # Función para ejecutar el comando de powershell con privilegios de administrador
    def run_powershell_command(self):

        # Crear la carpeta temp si no existe
        if not os.path.exists('C:\\temp'):
            os.makedirs('C:\\temp')

        # Comando de PowerShell
        command = "secedit /export /cfg C:\\temp\\secpol.inf"

        # Opciones para ocultar la ventana de la consola
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Ejecutar el comando de PowerShell
        try:
#            subprocess.run(["powershell", "-Command", "Start-Process powershell -ArgumentList '-Command {}' -Verb RunAs".format(command)], check=True)
            process = subprocess.Popen(["powershell", 
                                        "-Command", 
                                        command], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, 
                                        shell=False, startupinfo=startupinfo
                                        ).communicate()
#            process.communicate()
        except subprocess.CalledProcessError as e:
            print(f"Hubo un problema al ejecutar el script de PowerShell: {str(e)}")