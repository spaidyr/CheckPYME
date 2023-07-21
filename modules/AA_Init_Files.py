import subprocess
import os
from datetime import datetime
import platform
import pytz

class AA_Init_Files():

    def __init__(self) -> dict:
        self.result = {}
        name = 'AA_Init_Files'
        self.result['module_name'] = name
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = self.check()

    def check(self):
        
        self.run_SecPol()
        self.run_GpResult()

    # Función para ejecutar el comando de powershell con privilegios de administrador
    def run_SecPol(self):

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
    
    def run_GpResult(self):

        # Crear la carpeta temp si no existe
        if not os.path.exists('C:\\temp'):
            os.makedirs('C:\\temp')

        # Comando de PowerShell
        #command = "cd C: ; cd temp ; del .\report.html ; gpresult /h report.html"
        command = "cd C: ; cd temp ; gpresult /h report.html"

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