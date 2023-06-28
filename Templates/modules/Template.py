# Importación de las bibliotecas necesarias
from datetime import datetime
import platform
import pytz

# El nombre de la clase debe coincidir con el nombre del archivo

class Template():
    """
    La clase Template inicializa y organiza la información relevante del módulo y del sistema.

    Atributos
    ----------
    result : dict
        Un diccionario que contiene la información de seguridad que se desea enviar a Elasticsearch.

    Métodos
    -------
    __init__():
        Inicializa los atributos de la clase.
    check():
        Devuelve el diccionario con la información actualizada.
    """

    def __init__(self) -> dict:
        """
        Constructor de la clase. Inicializa el atributo 'result' con el nombre del módulo, 
        el nombre del host y la marca de tiempo actual en la zona horaria de Madrid.
        """
        self.result = {}
        name = 'Template'                                               # Debe tener el mismo nombre que la clase
        self.result['module_name'] = name
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')                      
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()  # Este dato está normalizado para ser compatible con Elasticsearch
        self.log_file = self.check()                                    # El agente llamará a este atributo para extraer la información

    def check(self):
        """
        Función de chequeo. Devuelve el diccionario 'result' actualizado.
        
        Nota: La funcionalidad específica del lado del cliente debe ser implementada aquí.
        """
        return self.result
