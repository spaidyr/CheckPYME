import json
import os
import importlib.util

TEMPLATE_PATH = './check/templates'
MODULE_CHECK_PATH = './check/modules'

def recived_doc(doc_file, policie, hostname):

    template = read_template(policie)
    policie_instance = import_policie_module(policie, doc_file, template)
    doc_low, doc_medium, doc_high, doc_security_status = policie_instance.get_result() 
#    doc_security_status = policie_instance.get_security_status()
    return doc_low, doc_medium, doc_high, doc_security_status
#    return doc_security_status

def read_template(policie):
    with open(os.path.join(TEMPLATE_PATH, f'{policie}.json'), "r") as f:
        return json.load(f)

def import_policie_module(policie, doc_file, template):
    module_path = os.path.join(MODULE_CHECK_PATH, f'{policie}.py')
    spec = importlib.util.spec_from_file_location(policie, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Crear una instancia de la clase y devolverla
    class_ = getattr(module, policie)  # Obtiene la clase del módulo
    policie_instance = class_(doc_file, template)  # Crea una instancia de la clase
    return policie_instance