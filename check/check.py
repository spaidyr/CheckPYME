import json
import os
import importlib.util

TEMPLATE_PATH = './check/templates'
MODULE_CHECK_PATH = './check/modules'

def recived_doc(doc_file, policie, hostname):
    """
    Procesa un documento recibido de acuerdo a una política específica.

    Parámetros
    ----------
    doc_file : str
        Documento de Elasticsearch a procesar.
    policie : str
        El nombre de la política a consultar.
    hostname : str
        El nombre del host a consultar.

    Retorna
    -------
    tuple
        Un tuple que contiene el número de incidencias de baja, media y alta seguridad, 
        así como el estado de seguridad del equipo en esa política concreta.
    """
    template = read_template(policie)
    policie_instance = import_policie_module(policie, doc_file, template)
    doc_low, doc_medium, doc_high, doc_security_status = policie_instance.get_result() 
    return doc_low, doc_medium, doc_high, doc_security_status

def read_template(policie):
    """
    Lee el archivo de plantilla JSON para una política específica.

    Parámetros
    ----------
    policie : str
        El nombre de la política.

    Retorna
    -------
    dict
        Un diccionario que representa la plantilla JSON correspondiente a la política.
    """
    with open(os.path.join(TEMPLATE_PATH, f'{policie}.json'), "r") as f:
        return json.load(f)

def import_policie_module(policie, doc_file, template):
    """
    Importa el módulo de política especificado y crea una instancia de la clase de política.

    Parámetros
    ----------
    policie : str
        El nombre de la política.
    doc_file : str
        Documento de Elasticsearch a procesar.
    template : dict
        El diccionario que representa la plantilla JSON.

    Retorna
    -------
    object
        Una instancia de la clase de política que se ha consultado.
    """
    module_path = os.path.join(MODULE_CHECK_PATH, f'{policie}.py')
    spec = importlib.util.spec_from_file_location(policie, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Crear una instancia de la clase y devolverla
    class_ = getattr(module, policie)  # Obtiene la clase del módulo
    policie_instance = class_(doc_file, template)  # Crea una instancia de la clase
    return policie_instance