import socket
import threading
import uuid
import os
import sqlite.db as db
from datetime import datetime
import json

clients = db.init_db()
server_running = True
server_socket = None

def start_server():
    global server_socket
    global server_running
    host = '127.0.0.1'
    port = 6605
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.settimeout(1)  # Establece un tiempo de espera de 1 segundo
    server_socket.listen()
    print(f"Servidor escuchando en {host}:{port}")

    while server_running:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
        except socket.timeout:
            pass
    
    server_socket.close()

def stop_server():
    global server_running
    server_running = False
    

def handle_client(client_socket, client_address):
    received_data = client_socket.recv(1024).decode('utf-8')
    received_token, hostname = received_data.split('|')
    
    if received_token in clients and clients[received_token]['hostname'] == hostname:
        actualizar_cliente(client_address, received_token, client_socket, hostname)
        client_socket.send('True'.encode('utf-8'))
    else:
        value = True
        for index in clients.values():
            if index['hostname'] == hostname:
                value = False
        if value:
            new_token = generar_token()
            while new_token in clients:  # Asegurar que el token no se repita
                new_token = generar_token()
            registrar_cliente(client_address, new_token, client_socket, hostname)
            client_socket.send(new_token.encode('utf-8'))
        else:
            client_socket.send('False'.encode('utf-8'))
    
    for client in clients:
        print(client, clients[client])

    # Recibir y guardar archivo JSON del cliente
    if not os.path.exists(f'logs/{clients[received_token]["hostname"]}'):
            os.makedirs(f'logs/{clients[received_token]["hostname"]}')
    # 
    recibir_log(received_token, client_socket)

    client_socket.close()

import json

def recibir_log(received_token, client_socket):
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(f'logs/{clients[received_token]["hostname"]}/scan_{now}.json')
    
    # Recibir todos los datos del cliente
    received_data = b''
    data = client_socket.recv(1024)
    while data:
        received_data += data
        data = client_socket.recv(1024)
    
    # Convertir los datos recibidos a diccionarios
    decoded_data = received_data.decode('utf-8')
    received_dicts = [json.loads(chunk) for chunk in decoded_data.split('\n') if chunk]
    
    # Combinar todos los diccionarios en uno solo
    combined_dict = {}
    for d in received_dicts:
        combined_dict.update(d)
    
    # Guardar el diccionario combinado en un archivo JSON con el formato deseado
    with open(log_file, 'w') as file:
        json.dump(combined_dict, file, indent=4, ensure_ascii=False)

def generar_token():
    return str(uuid.uuid4())

def registrar_cliente(client_address, token, client_socket, hostname):
    clients[token] = {'hostname': hostname, 'address': client_address[0], 'socket': client_socket}
    db.update_db_with_new_client(token, hostname, client_address[0])

def actualizar_cliente(client_address, token, client_socket, hostname):
    clients[token]['address'] = client_address[0]
    clients[token]['socket'] = client_socket
    clients[token]['hostname'] = hostname

def listar_clientes():
    online_clients = {}
    for token, client_data in clients.items():
        if client_data:
            online = check_client_online(client_data['address'], token)
        else:
            online = False
        online_clients[token] = {**client_data, 'online': online}
    return online_clients

def check_client_online(host, token):
    port = 6610
    try:
        checking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        checking_socket.settimeout(2)
        checking_socket.connect((host, port))
        checking_socket.send("validate_token".encode('utf-8'))
        response = checking_socket.recv(1024).decode('utf-8')
        if response == token:
            checking_socket.send("Validated".encode('utf-8'))
        else:
            checking_socket.send("NOT Validated".encode('utf-8'))
        checking_socket.close()
        return response == token
    except (socket.error, socket.timeout):
        return False