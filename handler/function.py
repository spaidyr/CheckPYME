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
    server_thread = threading.Thread(target=socket_handler.start_server).start()

def stop_server():
    socket_handler.stop_server()

def get_server_ip():
    config = socket_handler.read_config()
    return config["configuration"][0]["server_ip"]

def list_clients():
    content = 'Hello'
    online_clients = socket_handler.sendToEveryClient(content)
    return online_clients

# Esta duncion solo funciona con cly.py, no está en uso en MyApp
def confirm_exit():
    while True:
        confirmacion = input("Are you sure you want to shut down the server? (y/n): ").lower()
        if confirmacion == "y":
            return True
        elif confirmacion == "n":
            return False
        else:
            print("Invalid option. Please try again.")

def excute_modules():
    content = 'exec_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def update_clients():
    content = 'update_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def delete_client(hostname):
    result = socket_handler.delete_client(hostname)
    return result

def check_files():
    mod_times = get_mod_times()
    for file, mod_time in mod_times.items():
        if file not in last_mod_times or last_mod_times[file] != mod_time:
            last_mod_times = mod_times  # Update stored mod times
            return True
    return False

def get_mod_times():
        mod_times = {}
        for file in os.listdir("./modules"):
            if file.endswith(".py"):  # Check only python files
                mod_times[file] = os.path.getmtime("./modules/" + file)
        return mod_times

def get_server_running():
    server_running = socket_handler.get_server_running()
    return server_running

def generate_certificates():
    config = certs.read_config()
    ca_private_key, ca_cert = certs.generate_ca(config)
    if ca_private_key and ca_cert:
        client_private_key, client_cert = certs.generate_client_key_cert(ca_private_key, ca_cert, config)
        server_private_key, server_cert = certs.generate_server_key_cert(ca_private_key, ca_cert, config)

def copy_file(src_path, dest_path):
    try:
        shutil.copy2(src_path, dest_path)
        print(f"El archivo ha sido copiado de {src_path} a {dest_path} con éxito.")
    except Exception as e:
        print(f"Ha ocurrido un error al copiar el archivo: {e}")

def start_elasticsearch():
    global ELASTICSEARCH_THREAD
    try:
        cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch"'
        ELASTICSEARCH_THREAD = threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
        print("Se ha iniciado Elasticsearch correctamente.")        
    except Exception as e:
        print(f"Ha ocurrido un error al iniciar Elasticsearch: {e}")

def start_kibana():
    global KIBANA_THREAD
    try:
        cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\bin\\kibana"'
        KIBANA_THREAD = threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
        
        print("Se ha iniciado Kibana correctamente.")
    except Exception as e:
        print(f"Ha ocurrido un error al iniciar Elasticsearch: {e}")
def check_and_create_index():
    elk.check_and_create_index()
    
def reset_elasticsearch_password():
    cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch-reset-password -u elastic -i"'
    threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start()
    
def reset_kibana_password():
    cmd = 'start cmd.exe @cmd /k "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\bin\\elasticsearch-reset-password -u kibana_system -i"'
    threading.Thread(target=lambda: subprocess.run(cmd, shell=True)).start() 

def write_file(file_path, updates):
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
    
    check_iterator(module_list)

def check_iterator(module_list):
    for policie in module_list:
            for client, client_data in clients.items():
                doc_file = elk.get_checkpyme(policie, client_data["hostname"], INDEX_NAME)
                # print(doc_file)
                doc_low, doc_medium, doc_high, doc_security_status = analize(doc_file, policie, client_data["hostname"])
        #        analize(doc_file, policie, client_data["hostname"])
                elk.post_results(doc_low, INDEX_RESULT)
                elk.post_results(doc_medium, INDEX_RESULT)
                elk.post_results(doc_high, INDEX_RESULT)
                elk.post_results(doc_security_status, INDEX_STATUS)

def compliance_STIC(hostname):
    config = socket_handler.config
    modules = config['modules']

    total_counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}

    for module in modules:
        for key in module:
            response = elk.get_checkpyme(key, hostname, INDEX_STATUS)
            # Get the '_source' data
            counters = get_list_counters(response)
            total_counters = {key: total_counters[key] + counters[key] for key in total_counters}
    
    value = get_min_value(total_counters)
    return value

def compliance_custom(hostname):
    config = socket_handler.read_config()
    modules = config.get("modules", [])
    total_counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}
    for module in modules:
        for key, status in module.items():
            if status.lower() == "true":
                response = elk.get_checkpyme(key, hostname, INDEX_STATUS)
                # Get the '_source' data
                counters = get_list_counters(response)
                total_counters = {key: total_counters[key] + counters[key] for key in total_counters}
    value = get_min_value(total_counters)
    return value    
    
    


def get_policie(hostname, policie):
    response = elk.get_checkpyme(policie, hostname, INDEX_STATUS)
    source_data = response.get('_source', {})
    # Convertimos el diccionario a una lista de items (pares clave-valor)
    items = list(source_data.items())
    # Removemos las tres primeras y la última clave
    items = items[3:-1]
    # Volvemos a convertir la lista de items a un diccionario
    final_dict = dict(items)
    return final_dict

def get_status_policie(policie, hostname):
    respone = elk.get_checkpyme(policie, hostname, INDEX_STATUS)
    counters = get_list_counters(respone)
    status = get_min_value(counters)
    return status

def get_booleans_security(hostname, security_level):
    config = socket_handler.config
    modules = config['modules']

    counters = { True:0, False:0}

    for module in modules:
        for key in module:
            response = elk.get_checkpyme_compliance(key, hostname, security_level)
            source_data = response.get('_source', {})
            for value in source_data.values():
                if value in counters:
                    counters[value] += 1
    return counters

def get_booleans_policie(hostname, policie, security_level):
    counters = { True:0, False:0}
    response = elk.get_checkpyme_compliance(policie, hostname, security_level)
    source_data = response.get('_source', {})
    for value in source_data.values():
        if value in counters:
            counters[value] += 1
    return counters
def get_list_counters(response):
    
     # Initialize the counters
    counters = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}

    source_data = response.get('_source', {})
    for value in source_data.values():
        if value.lower() in counters:
            counters[value.lower()] += 1

    # Return a dictionary with the counter values
    return counters

def get_min_value(counters):
    if counters["none"] > 0:
        return 'None'
    elif counters["low"] > 0:
        return 'low'
    elif counters["medium"] > 0:
        return 'medium'
    elif counters["high"] > 0:
        return 'high'

def read_config():
    return socket_handler.config