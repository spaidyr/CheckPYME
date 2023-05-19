import socket
import os
import importlib
import time
import platform
import threading
import json
from cryptography.fernet import Fernet
import base64
import ssl

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)

def start_client(config):

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
    if received_data == "validate_token":
        validate_token(server_socket)
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
    if response == "Validated":
        print('OK, the Token is ',response)
    else:
        print(response)

def get_module_files(directory):
    with os.scandir(directory) as entries:
        return tuple(entry.name for entry in entries if entry.is_file() and entry.name.endswith('.py'))

def load_modules():
    module_directory = 'modules'
    module_files = get_module_files(module_directory)
    modules = import_modules(module_directory, module_files)
    for module in modules:
        module_name = module.__name__
        module_path, module_class = module_name.split('.')
        log_file = getattr(module, module_class)().log_file

        log_path = os.path.join("agent.json")
        with open(log_path, 'a') as file:
             json.dump(log_file, file, ensure_ascii=False)
             file.write('\n')

def import_modules(module_directory, module_files):
    imported_modules = []
    for module_file in module_files:
        module_name = os.path.splitext(module_file)[0]  # Elimina la extensión '.py'
        module_path = f"{module_directory}.{module_name}"
        imported_module = importlib.import_module(module_path)
        imported_modules.append(imported_module)

    return imported_modules


if __name__ == '__main__':
    config = read_config()
    start_client(config)
    threading.Thread(target=listen_for_server(config)).start()