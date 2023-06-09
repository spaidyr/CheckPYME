import socket
import os
import importlib
import time
import platform
import threading
import json
from elasticsearch import Elasticsearch
from cryptography.fernet import Fernet
import base64
import ssl
import shutil
import os

def start_client(config_file):

    global config
    config = config_file
    # Socket Server

    host = config["server_ip"]
    port = int(config["server_port"])
    # Crea un socket de cliente no seguro
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Envuelve el socket del cliente con SSL
    client_socket = ssl.wrap_socket(
        client_socket, 
        certfile='./certs/client.crt', 
        keyfile='./certs/client.key',
        ca_certs='./certs/ca.crt',
        cert_reqs=ssl.CERT_REQUIRED
        )
    token = load_encrypted_token()
    hostname = platform.node()

    # Intenta conectarse al servidor hasta que tenga éxito
    while True:
        try:
            client_socket.connect((host, port))
            break
        except socket.error:
            print("No se pudo conectar al servidor. Reintentando en 5 segundos...")
            time.sleep(5)

    handle_server_response(client_socket, token, hostname)

def listen_for_server(config):

    host = socket.gethostbyname(socket.gethostname())
    port = int(config["client_port"])
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Envuelve el socket de escucha con SSL
    listening_socket = ssl.wrap_socket(
        listening_socket,
        certfile='./certs/client.crt', 
        keyfile='./certs/client.key',
        ca_certs='./certs/ca.crt',
        cert_reqs=ssl.CERT_REQUIRED,
        server_side=True
        )
    listening_socket.bind((host, port))
    listening_socket.listen()

    while True:
        server_socket, _ = listening_socket.accept()
        threading.Thread(target=handle_server_request, args=(server_socket,)).start()

def handle_server_request(server_socket):
    received_data = server_socket.recv(1024).decode('utf-8')
    if received_data == "Hello":
        validate_token(server_socket)
    elif received_data == "exec_modules":
        load_modules()
        server_socket.send('Success'.encode('utf-8'))
    elif received_data == "update_modules":
        response = server_socket.recv(10240).decode('utf-8')
        if response.startswith('UPDATE_MODULES'):
            new_modules_data = response.split('UPDATE_MODULES')[1]
            update_modules(new_modules_data)
        server_socket.send('Success'.encode('utf-8'))
    server_socket.close()

def handle_server_response(client_socket, token, hostname):
    if token:
        client_socket.send(f"{token}|{hostname}".encode('utf-8'))
    else:
        client_socket.send(f"None|{hostname}".encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')

    if response == 'False':
        print('El token proporcionado no coincide con el hostname')
    else:
        if response == 'True':
            print('Token confirmado por el servidor')
        else:
            store_encrypted_token(response)
            print(f'Token actualizado: {response}')
    
    response = client_socket.recv(10240).decode('utf-8')
    if response.startswith('UPDATE_MODULES'):
        new_modules_data = response.split('UPDATE_MODULES')[1]
        update_modules(new_modules_data)
    else:
        load_modules()

    client_socket.close()

# Genera una clave y guárdala en un archivo seguro (solo la primera vez, luego reutiliza la misma clave)
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Carga la clave desde el archivo
def load_key():
    if not os.path.exists("key.key"):
        generate_key()
    with open("key.key", "rb") as key_file:
        return key_file.read()

def encrypt_token(token):
    key = load_key()
    f = Fernet(key)
    return f.encrypt(token.encode())

def decrypt_token(encrypted_token):
    key = load_key()
    f = Fernet(key)
    return f.decrypt(encrypted_token).decode()

# Guarda el token cifrado en el archivo 'token.txt'
def store_encrypted_token(token):
    encrypted_token = encrypt_token(token)
    base64_encrypted_token = base64.b64encode(encrypted_token)
    with open('token.bin', 'wb') as file:
        file.write(base64_encrypted_token)
    encrypt_and_store_credentials()

# Carga y descifra el token desde el archivo 'token.txt'
def load_encrypted_token():
    if os.path.exists('token.bin'):
        with open('token.bin', 'rb') as file:
            base64_encrypted_token = file.read()
            encrypted_token = base64.b64decode(base64_encrypted_token)
            return decrypt_token(encrypted_token)
    return None

def validate_token(server_socket):
    token = load_encrypted_token()
    if token is None:
        print("No se encontró el token")
        return
    print(f"Validando token {token}")
    server_socket.send(token.encode('utf-8'))
    response = server_socket.recv(1024).decode('utf-8')
    if response == "Authorized":
        print(response, ' OK')
    else:
        print(response)

def get_module_files(directory):
    with os.scandir(directory) as entries:
        return tuple(entry.name for entry in entries if entry.is_file() and entry.name.endswith('.py'))

def load_modules():
    module_directory = './modules'
    module_files = get_module_files(module_directory)
    modules = import_modules(module_directory, module_files)
    for module in modules:
        importlib.reload(module)  # Aquí se recarga el módulo
        module_name = module.__name__
        module_path, module_class = module_name.split('.')
        log_file = getattr(module, module_class)().log_file

        log_path = os.path.join("agent.json")
        with open(log_path, 'a') as file:
             json.dump(log_file, file, ensure_ascii=False)
             file.write('\n')
        
        # Post to Elasticsearch
        post_to_elasticsearch(log_file)

imported_modules = set()

def import_modules(module_directory, module_files):
    imported_modules = []
    for module_file in module_files:
        module_name = os.path.splitext(module_file)[0]  # Elimina la extensión '.py'
        module_path = f"{module_directory}.{module_name}"
        module_path = module_path.replace('./', '')  # Elimina './'
        imported_module = importlib.import_module(module_path)
        imported_modules.append(imported_module)

    return imported_modules

def update_modules(new_modules_data):
    # Convertimos los datos recibidos a diccionario
    new_modules = json.loads(new_modules_data)

    # Borrar todos los archivos en el directorio de módulos
    module_directory = './modules'
    for filename in os.listdir(module_directory):
        file_path = os.path.join(module_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    for module_name, module_content in new_modules.items():
        # Guardamos el nuevo módulo, reemplazando el antiguo
        with open(f'./modules/{module_name}', 'w') as f:
            f.write(module_content)

    print("Módulos actualizados exitosamente")

def encrypt_and_store_credentials():
    if os.path.exists('elk_credentials.txt'):
        with open('elk_credentials.txt', 'r') as file:
            credentials = file.read()
            
        encrypted_credentials = encrypt_token(credentials)
        base64_encrypted_credentials = base64.b64encode(encrypted_credentials)
        with open('elk.bin', 'wb') as file:
            file.write(base64_encrypted_credentials)
        
        os.remove('elk_credentials.txt')
        print("Credenciales encriptadas y guardadas exitosamente en 'elk.bin'")
    else:
        print("No se encontró el archivo 'elk_credentials.txt'")

def load_and_decrypt_credentials():
    if os.path.exists('elk.bin'):
        with open('elk.bin', 'rb') as file:
            base64_encrypted_credentials = file.read()
            encrypted_credentials = base64.b64decode(base64_encrypted_credentials)
            return decrypt_token(encrypted_credentials)
    else:
        print("No se encontró el archivo 'elk.bin'")
    return None

def post_to_elasticsearch(log_data):
    host = config["server_ip"]
    credentials = load_and_decrypt_credentials().split(':')
    es = Elasticsearch(
        [f'https://{host}:9200'],
        verify_certs=True,
        ca_certs='./certs/ca.crt',
        basic_auth=(credentials[0], credentials[1])
    )
    
    # Realiza la operación de indexación
    es.index(index='checkpyme', document=log_data)