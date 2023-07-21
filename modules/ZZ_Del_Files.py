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
        path = "C:\\temp"
        sepcol = "secpol.inf"
        gpresult = "report.html"
        self.delete_files(path, sepcol, gpresult)

    def delete_files(self, path, file1, file2):
        """
        Elimina dos archivos de una ruta específica.

        Argumentos:
            path (str): La ruta donde se encuentran los archivos.
            file1 (str): El nombre del primer archivo a eliminar.
            file2 (str): El nombre del segundo archivo a eliminar.

        Devuelve:
            str: un mensaje que indica si los archivos fueron eliminados con éxito o no.
        """
        try:
            os.remove(os.path.join(path, file1))
            os.remove(os.path.join(path, file2))
            return f"Los archivos {file1} y {file2} han sido eliminados con éxito."
        except FileNotFoundError as fnf_error:
            return str(fnf_error)
        except Exception as e:
            return str(e)
