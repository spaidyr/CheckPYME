import os
import requests
import zipfile
import subprocess

# Definimos los paths donde se instalarán Elasticsearch y Kibana
ELASTICSEARCH_PATH = "C:\\Elastic\\Elasticsearch\\8.8.0"
KIBANA_PATH = "C:\\Elastic\\Kibana\\8.8.0"

# URLs de las versiones 8.8.0 de Elasticsearch y Kibana para Windows
ELASTICSEARCH_URL = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.8.0-windows-x86_64.zip"
KIBANA_URL = "https://artifacts.elastic.co/downloads/kibana/kibana-8.8.0-windows-x86_64.zip"

# Archivos donde se guardarán los instaladores descargados
ELASTICSEARCH_ZIP = "elasticsearch-8.8.0-windows-x86_64.zip"
KIBANA_ZIP = "kibana-8.8.0-windows-x86_64.zip"

# Archivos de configuración
ELASTICSEARCH_YML = 'C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\config\\elasticsearch.yml'
KIBANA_YML = 'C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\\kibana.yml'

def main(dialog):
    """
    Función principal que inicia la descarga, instalación y configuración de Elasticsearch y Kibana.
    
    Parámetros:
    dialog (QDialog, opcional): Un diálogo Qt que muestra el progreso de la instalación.
    """
    if not __is_elasticsearch_installed():
        try:
            if dialog:
                dialog.setLabelText('Installing Elasticsearch...')
            __install_elasticsearch()
            __update_elastic_config(ELASTICSEARCH_YML)
            __remove_zip(ELASTICSEARCH_ZIP)  # Elimina el .zip de Elasticsearch después de una instalación exitosa
        except:
            print("Error when install Elasticsearch")
    else:
        print("Elasticsearch is already installed.")

    if not __is_kibana_installed():
        try:
            if dialog:
                dialog.setLabelText('Installing Kibana...')
            __install_kibana()
            __update_kibana_config(KIBANA_YML)
            __remove_zip(KIBANA_ZIP)  # Elimina el .zip de Kibana después de una instalación exitosa
        except:
            print("Error when install Kibana")
    else:
        print("Kibana is already installed.")
    
    if dialog:
        dialog.close()

def __download_file(url, local_filename):
    """
    Descarga un archivo de una URL dada y lo guarda en un directorio local especificado.
    
    Parámetros:
    url (str): La URL del archivo que se descargará.
    local_filename (str): La ruta del archivo local donde se guardará el archivo descargado.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

def __extract_zip(file_path, extract_path):
    """
    Extrae un archivo zip a un directorio específico.
    
    Parámetros:
    file_path (str): La ruta del archivo zip que se extraerá.
    extract_path (str): El directorio donde se extraerán los archivos.
    """
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def __install_elasticsearch():
    """
    Descarga, extrae e instala Elasticsearch si aún no está instalado.
    También agrega una contraseña segura al keystore de Elasticsearch.
    """
    if not os.path.isfile(ELASTICSEARCH_ZIP):
        print("Downloading Elasticsearch...")
        __download_file(ELASTICSEARCH_URL, ELASTICSEARCH_ZIP)

    print("Extracting and installing Elasticsearch...")
    __extract_zip(ELASTICSEARCH_ZIP, ELASTICSEARCH_PATH)
    __add_secure_password_to_keystore('elastic')

def __add_secure_password_to_keystore(password):
    """
    Agrega una contraseña segura al keystore de Elasticsearch.
    
    Parámetros:
    password (str): La contraseña que se agregará al keystore.
    """
    try:
        # Primero, inicia el keystore si aún no está iniciado
        subprocess.run(["elasticsearch-keystore", "create"], check=True)

        # A continuación, utiliza un proceso para enviar la contraseña al keystore
        process = subprocess.Popen(["elasticsearch-keystore", "add", "xpack.security.http.ssl.keystore.secure_password"],
                                   stdin=subprocess.PIPE)
        process.communicate(password.encode())  # Envía la contraseña al proceso
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        
        print("Se agregó la contraseña de manera segura al keystore de Elasticsearch.")
    except Exception as e:
        print(f"Ha ocurrido un error al agregar la contraseña al keystore: {e}")

def __install_kibana():
    """
    Descarga, extrae e instala Kibana si aún no está instalado.
    """
    if not os.path.isfile(KIBANA_ZIP):
        print("Downloading Kibana...")
        __download_file(KIBANA_URL, KIBANA_ZIP)

    print("Extracting and installing Kibana...")
    __extract_zip(KIBANA_ZIP, KIBANA_PATH)

def __is_elasticsearch_installed():
    """
    Comprueba si Elasticsearch ya está instalado.
    
    Devoluciones:
    bool: Verdadero si Elasticsearch ya está instalado, falso de lo contrario.
    """
    # Comprobar si existe el directorio de instalación de Elasticsearch
    return os.path.isdir(ELASTICSEARCH_PATH)

def __is_kibana_installed():
    """
    Comprueba si Kibana ya está instalado.
    
    Devoluciones:
    bool: Verdadero si Kibana ya está instalado, falso de lo contrario.
    """
    # Comprobar si existe el directorio de instalación de Kibana
    return os.path.isdir(KIBANA_PATH)

def __update_elastic_config(file_path):
    """
    Actualiza la configuración de Elasticsearch en el archivo .yml.
    
    Parámetros:
    file_path (str): La ruta del archivo de configuración .yml.
    """
    # Define the updates
    updates = {
        '#cluster.name: my-application': 'cluster.name: CheckPYME',
        '#node.name: node-1': 'node.name: node-1',
        '#network.host: 192.168.0.1': 'network.host: 0.0.0.0',
        '#cluster.initial_master_nodes: ["node-1", "node-2"]': 'cluster.initial_master_nodes: ["node-1"]'
    }

    # Add new lines at the end
    new_lines = [
        'xpack.security.enabled: true',
        'xpack.security.http.ssl.enabled: true',
        'xpack.security.transport.ssl.enabled: true',
        'xpack.security.http.ssl.key: server.key',
        'xpack.security.http.ssl.certificate: server.crt',
        'xpack.security.http.ssl.certificate_authorities: ca.crt',
        'xpack.security.transport.ssl.key: server.key',
        'xpack.security.transport.ssl.certificate: server.crt',
        'xpack.security.transport.ssl.certificate_authorities: ca.crt'
    ]
    __write_file(file_path, updates, new_lines)    

def  __update_kibana_config(file_path):
    """
    Actualiza la configuración de Kibana en el archivo .yml.
    
    Parámetros:
    file_path (str): La ruta del archivo de configuración .yml.
    """
    # Define the updates
    updates = {
        '#server.host: "localhost"': 'server.host: "127.0.0.1"',
        '#elasticsearch.hosts: ["http://localhost:9200"]': 'elasticsearch.hosts: ["https://127.0.0.1:9200"]',
        '#server.ssl.enabled: false': 'server.ssl.enabled: true',
        '#server.ssl.certificate: /path/to/your/server.crt': 'server.ssl.certificate: C:\Elastic\Kibana\8.8.0\kibana-8.8.0\config\server.crt',
        '#server.ssl.key: /path/to/your/server.key': 'server.ssl.key: C:\Elastic\Kibana\8.8.0\kibana-8.8.0\config\server.key',
        '#elasticsearch.ssl.certificateAuthorities: [ "/path/to/your/CA.pem" ]': 'elasticsearch.ssl.certificateAuthorities: [ "C://Elastic//Kibana//8.8.0//kibana-8.8.0//config//ca.crt" ]',
        '#elasticsearch.username: "kibana_system"': 'elasticsearch.username: "kibana_system"',
        '#elasticsearch.password: "pass"': 'elasticsearch.password: "elastic"',
        '#elasticsearch.ssl.verificationMode: full': 'elasticsearch.ssl.verificationMode: full'
    }

    # Add new lines at the end
    new_lines = []
    __write_file(file_path, updates, new_lines)

def __write_file(file_path, updates, new_lines):
    """
    Escribe líneas en un archivo.
    
    Parámetros:
    file_path (str): La ruta del archivo donde se deben escribir las líneas.
    updates (dict): Un diccionario de las líneas que deben ser actualizadas.
    new_lines (list): Una lista de nuevas líneas que deben ser añadidas al final del archivo.
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

        # Add a newline character to the end of the file if not present
        if lines and not lines[-1].endswith('\n'):
            file.write('\n')

        # Check if new line exists
        for new_line in new_lines:
            # We need to add '\n' to new_line to match the format in lines
            if (new_line + '\n') not in lines:
                file.write(new_line + '\n')

def __remove_zip(file_path):
    """
    Elimina el archivo .zip especificado.
    
    Parámetros:
    file_path (str): La ruta del archivo .zip a eliminar.
    """
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"{file_path} ha sido eliminado con éxito.")
        except Exception as e:
            print(f"Error al eliminar el archivo {file_path}: {e}")
