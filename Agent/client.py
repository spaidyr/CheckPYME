import socket
import os
import importlib
import time
import platform
import threading
import json
from cryptography.fernet import Fernet

def start_client():

    # Socket Server

    host = '127.0.0.1'
    port = 6605
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

def listen_for_server():
    host = '127.0.0.1'
    port = 6610
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    if response == 'True':
        print('Token confirmado por el servidor')
    elif response == 'False':
        print('El token proporcionado no coincide con el hostname')
    else:
        save_encrypted_token(response)
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
    with open("key.key", "rb") as key_file:
        key = key_file.read()
    return key

# Guarda el token cifrado en el archivo 'token.txt'
def save_encrypted_token(token):
    if not os.path.exists("key.key"):
        generate_key()
    key = load_key()
    cipher_suite = Fernet(key)
    encrypted_token = cipher_suite.encrypt(token.encode())

    with open("token.txt", "wb") as file:
        file.write(encrypted_token)

# Carga y descifra el token desde el archivo 'token.txt'
def load_encrypted_token():
    if os.path.exists("token.txt"):
        key = load_key()
        cipher_suite = Fernet(key)

        with open("token.txt", "rb") as file:
            encrypted_token = file.read()
            token = cipher_suite.decrypt(encrypted_token).decode()
            return token
    return None

def validate_token(server_socket):
    token = load_encrypted_token()
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
    start_client()
    threading.Thread(target=listen_for_server).start()