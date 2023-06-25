import handler.socket_handler as socket_handler
import os
from handler.socket_handler import clients
import handler.elastic_handler as elk
import certs.certs as certs
import shutil
import subprocess
import threading
from check.check import recived_doc as analize

INDEX_NAME = 'checkpyme-agents'
INDEX_RESULT = 'checkpyme-results-levels'
INDEX_STATUS = 'checkpyme-results-status'

def sart_server():
    """
    Inicia el servidor iniciando un nuevo hilo y llamando a la función start_server en el controlador de sockets.
    """
    server_thread = threading.Thread(target=socket_handler.start_server).start()

def stop_server():
    """
    Detiene el servidor llamando a la función stop_server en el controlador de sockets.
    """
    socket_handler.stop_server()

def get_server_ip():
    """
    Obtiene la dirección IP del servidor desde el archivo de configuración.

    Devuelve:
        str: Dirección IP del servidor.
    """
    config = socket_handler.read_config()
    return config["configuration"][0]["server_ip"]

def get_list_clients():
    """
    Envía un mensaje de "Hello" a todos los clientes conectados y devuelve una lista de los clientes online.

    Devuelve:
        dict: Un diccionario de los clientes online y sus detalles.
    """
    content = 'Hello'
    online_clients = socket_handler.sendToEveryClient(content)
    return online_clients

def excute_modules():
    """
    Envia la señal 'exec_modules' a todos los clientes conectados.

    Devuelve:
        dict: Un diccionario de los clientes y los resultados de la operación de envío.
    """
    content = 'exec_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def update_clients():
    """
    Envia la señal 'update_modules' a todos los clientes conectados.

    Devuelve:
        dict: Un diccionario de los clientes y los resultados de la operación de envío.
    """
    content = 'update_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def delete_client(hostname):
    """
    Elimina un cliente específico.

    Argumentos:
        hostname (str): El nombre del host del cliente a eliminar.

    Devuelve:
        bool: Verdadero si el cliente se elimina con éxito, Falso de lo contrario.
    """
    result = socket_handler.delete_client(hostname)
    return result

def check_files():
    """
    Comprueba si hay cambios en los archivos del directorio "./modules".

    Devuelve:
        bool: Verdadero si se detectan cambios, Falso de lo contrario.
    """
    mod_times = get_mod_times()
    for file, mod_time in mod_times.items():
        if file not in last_mod_times or last_mod_times[file] != mod_time:
            last_mod_times = mod_times  # Update stored mod times
            return True
    return False

def get_mod_times():
    """
    Obtiene los tiempos de modificación de los archivos de python en el directorio "./modules".

    Devuelve:
        dict: Un diccionario con los nombres de los archivos y sus respectivos tiempos de modificación.
    """
    mod_times = {}
    for file in os.listdir("./modules"):
        if file.endswith(".py"):  # Check only python files
            mod_times[file] = os.path.getmtime("./modules/" + file)
    return mod_times

def get_server_running():
    """
    Obtiene el estado de ejecución del servidor.

    Devuelve:
        bool: Verdadero si el servidor está en ejecución, Falso en caso contrario.
    """
    server_running = socket_handler.get_server_running()
    return server_running

def generate_certificates():
    """
    Genera los certificados CA, cliente y servidor utilizando la configuración del módulo de certificados.
    """
    config = certs.read_config()
    ca_private_key, ca_cert = certs.generate_ca(config)
    if ca_private_key and ca_cert:
        client_private_key, client_cert = certs.generate_client_key_cert(ca_private_key, ca_cert, config)
        server_private_key, server_cert = certs.generate_server_key_cert(ca_private_key, ca_cert, config)

def copy_file(src_path, dest_path):
    """
    Copia un archivo de una ruta de origen a una ruta de destino.

    Argumentos:
        src_path (str): La ruta de origen del archivo.
        dest_path (str): La ruta de destino del archivo.
    """
    try:
        shutil.copy2(src_path, dest_path)
        print(f"El archivo ha sido copiado de {src_path} a {dest_path} con éxito.")
    except Exception as e:
        print(f"Ha ocurrido un error al copiar el archivo: {e}")

def start_elasticsearch():
    """
    Inicia Elasticsearch en un nuevo hilo utilizando el comando proporcionado.
    """
    global ELASTICSEARCH_THREAD
    try:
        cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch"'
        ELASTICSEARCH_THREAD = threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
        print("Se ha iniciado Elasticsearch correctamente.")        
    except Exception as e:
        print(f"Ha ocurrido un error al iniciar Elasticsearch: {e}")

def start_kibana():
    """
    Inicia Kibana en un nuevo hilo utilizando el comando proporcionado.
    """
    global KIBANA_THREAD
    try:
        cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\bin\\kibana"'
        KIBANA_THREAD = threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
        
        print("Se ha iniciado Kibana correctamente.")
    except Exception as e:
        print(f"Ha ocurrido un error al iniciar Elasticsearch: {e}")
def check_and_create_index():
    """
    Comprueba y crea un índice en Elasticsearch si no existe.

    Devuelve:
        dict: El resultado de la operación de creación del índice.
    """
    return elk.check_and_create_index()
    
def reset_elasticsearch_password():
    """
    Reinicia la contraseña del usuario "elastic" en Elasticsearch en un nuevo hilo utilizando el comando proporcionado.
    """
    cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch-reset-password -u elastic -i"'
    threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
    
def reset_kibana_password():
    """
    Reinicia la contraseña del usuario "kibana_system" en Elasticsearch en un nuevo hilo utilizando el comando proporcionado.
    """
    cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch-reset-password -u kibana_system -i"'
    threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start() 

def write_file(file_path, updates):
    """
    Escribe en un archivo proporcionado con las actualizaciones proporcionadas.

    Argumentos:
        file_path (str): La ruta del archivo a escribir.
        updates (dict): Un diccionario de las líneas a actualizar con su texto actualizado.
    """
    # Open the file and read the lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Open the file again for writing
    with open(file_path, 'w') as file:
        # Go through the lines
        for line in lines:
            # Check if the line should be updated
            if line.strip() in updates:
                # Write the updated line
                file.write(updates[line.strip()] + '\n')
            else:
                # Write the line as is
                file.write(line)

def check_certificates():
    """
    Comprueba si los archivos de certificado para la CA, el cliente y el servidor ya existen.

    Devuelve:
        tuple: Un tuple de booleanos que indican la existencia de los certificados CA, cliente y servidor.
    """
    ca_certs = False
    client_certs = False
    server_certs = False

    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\ca\ca.key") or os.path.exists(".\certs\ca\ca.crt"):
        print("Los archivos de la CA ya existen.")
        ca_certs = True

    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\client\client.key") or os.path.exists("\.certs\client\client.crt"):
        print("Los archivos del cliente ya existen.")
        client_certs = True
    
    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\server\server.key") or os.path.exists("\.certs\server\server.crt"):
        print("Los archivos del cliente ya existen.")
        server_certs = True

    return ca_certs, client_certs, server_certs

def check_security(parameter):
    """
    Comprueba la seguridad de los módulos.

    Argumentos:
        parameter (str): El parámetro que especifica el tipo de módulos a comprobar.
    """
    config = socket_handler.read_config()
    modules = config.get("modules", [])
    module_list = []
    if parameter == 'full':
        for module in modules:
            module_list.extend(module.keys())
    else:
        for module in modules:
            for module_name, status in module.items():
                if status.lower() == "true":
                    module_list.append(module_name)
    
    set_doc_iterator(module_list)

def set_doc_iterator(module_list):
    """
    Itera sobre la lista de políticas y los clientes y analiza y publica los resultados.

    Argumentos:
        module_list (list): La lista de políticas para iterar.
    """
    for policie in module_list:
            for client, client_data in clients.items():
                try:
                    doc_file = elk.get_doc(policie, client_data["hostname"], INDEX_NAME)
                    doc_low, doc_medium, doc_high, doc_security_status = analize(doc_file, policie, client_data["hostname"])
                    elk.set_doc(doc_low, INDEX_RESULT)
                    elk.set_doc(doc_medium, INDEX_RESULT)
                    elk.set_doc(doc_high, INDEX_RESULT)
                    elk.set_doc(doc_security_status, INDEX_STATUS)
                except:
                    print(f'NO SE ENCONTRÓ DOCUMENTO PARA {client_data["hostname"]}')
def get_compliance_full(hostname):
    """
    Realiza la conformidad STIC para un host dado.

    Argumentos:
        hostname (str): El nombre del host para el cual realizar la conformidad.

    Devuelve:
        str: El valor mínimo del contador de conformidad.
    """
    config = socket_handler.config
    modules = config['modules']

    total_counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}

    for module in modules:
        for key in module:
            response = elk.get_doc(key, hostname, INDEX_STATUS)
            # Get the '_source' data
            if response:
                counters = get_list_counters(response)
                total_counters = {key: total_counters[key] + counters[key] for key in total_counters}
    
    value = get_min_value(total_counters)
    return value

def get_compliance_custom(hostname):
    """
    Realiza la conformidad personalizada para un host dado.

    Argumentos:
        hostname (str): El nombre del host para el cual realizar la conformidad.

    Devuelve:
        str: El valor mínimo del contador de conformidad.
    """
    config = socket_handler.read_config()
    modules = config.get("modules", [])
    total_counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}
    for module in modules:
        for key, status in module.items():
            if status.lower() == "true":
                response = elk.get_doc(key, hostname, INDEX_STATUS)
                # Get the '_source' data
                if response:
                    counters = get_list_counters(response)
                    total_counters = {key: total_counters[key] + counters[key] for key in total_counters}
    value = get_min_value(total_counters)
    return value    

def get_policie(hostname, policie):
    """
    Obtiene una política específica para un host dado.

    Argumentos:
        hostname (str): El nombre del host.
        policie (str): La política a obtener.

    Devuelve:
        dict: El diccionario de la política.
    """
    response = elk.get_doc(policie, hostname, INDEX_STATUS)
    source_data = response.get('_source', {})
    # Convertimos el diccionario a una lista de items (pares clave-valor)
    items = list(source_data.items())
    # Removemos las tres primeras y la última clave
    items = items[3:-1]
    # Volvemos a convertir la lista de items a un diccionario
    final_dict = dict(items)
    return final_dict

def get_status_policie(policie, hostname):
    """
    Obtiene el estado de una política específica para un host dado.

    Argumentos:
        policie (str): La política a comprobar.
        hostname (str): El nombre del host.

    Devuelve:
        str: El estado de la política.
    """
    respone = elk.get_doc(policie, hostname, INDEX_STATUS)
    counters = get_list_counters(respone)
    status = get_min_value(counters)
    return status

def get_booleans_security(hostname, security_level):
    """
    Obtiene los contadores de booleanos para un nivel de seguridad dado en un host.

    Argumentos:
        hostname (str): El nombre del host.
        security_level (str): El nivel de seguridad.

    Devuelve:
        dict: Un diccionario de los contadores de booleanos.
    """
    config = socket_handler.config
    modules = config['modules']

    counters = { True:0, False:0}

    for module in modules:
        for key in module:
            response = elk.get_security_compliance(key, hostname, security_level)
            if response:
                source_data = response.get('_source', {})
                for value in source_data.values():
                    if value in counters:
                        counters[value] += 1
    return counters

def get_booleans_policie(hostname, policie, security_level):
    """
    Obtiene los contadores de booleanos para una política y un nivel de seguridad dados en un host.

    Argumentos:
        hostname (str): El nombre del host.
        policie (str): La política.
        security_level (str): El nivel de seguridad.

    Devuelve:
        dict: Un diccionario de los contadores de booleanos.
    """
    counters = { True:0, False:0}
    response = elk.get_security_compliance(policie, hostname, security_level)
    source_data = response.get('_source', {})
    for value in source_data.values():
        if value in counters:
            counters[value] += 1
    return counters
def get_list_counters(response):
    """
    Obtiene los contadores de la respuesta dada.

    Argumentos:
        response (dict): La respuesta de la que obtener los contadores.

    Devuelve:
        dict: Un diccionario de los contadores.
    """
    # Initialize the counters
    counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}

    source_data = response.get('_source', {})
    for value in source_data.values():
        if value.lower() in counters:
            counters[value.lower()] += 1

    # Return a dictionary with the counter values
    return counters

def get_min_value(counters):
    """
    Obtiene el valor mínimo de los contadores.

    Argumentos:
        counters (dict): Los contadores de los que obtener el valor mínimo.

    Devuelve:
        str: El valor mínimo de los contadores.
    """
    if counters["none"] > 0:
        return 'None'
    elif counters["low"] > 0:
        return 'low'
    elif counters["medium"] > 0:
        return 'medium'
    elif counters["high"] > 0:
        return 'high'

def get_config():
    """
    Lee la configuración del gestor de sockets.

    Devuelve:
        dict: La configuración del gestor de sockets.
    """
    return socket_handler.config