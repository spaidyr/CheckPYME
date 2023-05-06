import socket
import os
import importlib
import time
import platform
import threading
import json



def start_client():
    host = '127.0.0.1'
    port = 6605
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    token = load_token()
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

def load_token():
    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as file:
            token = file.read().strip()
            return token
    return None

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

def validate_token(server_socket):
    token = load_token()
    print(f"Validando token {token}")
    server_socket.send(token.encode('utf-8'))
    response = server_socket.recv(1024).decode('utf-8')
    if response == "Validated":
        print('OK, the Token is ',response)
    else:
        print(response)

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
        store_token(response)
        print(f'Token actualizado: {response}')

    load_modules()

#         # Enviar archivo JSON al servidor
#         with open(f'{log_path}', 'rb') as file:
#             client_socket.sendfile(file)

    client_socket.close()

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

def store_token(token):
    with open('token.txt', 'w') as file:
        file.write(token)

def get_module_files(directory):
    with os.scandir(directory) as entries:
        return tuple(entry.name for entry in entries if entry.is_file() and entry.name.endswith('.py'))

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
    
    
