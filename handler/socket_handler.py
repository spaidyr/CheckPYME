import socket
import threading
import uuid
import sqlite.db as db

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
        update_client(client_address, received_token, client_socket, hostname)
        client_socket.send('True'.encode('utf-8'))
    else:
        value = True
        for index in clients.values():
            if index['hostname'] == hostname:
                value = False
        if value:
            new_token = generate_token()
            while new_token in clients:  # Asegurar que el token no se repita
                new_token = generate_token()
            register_client(client_address, new_token, client_socket, hostname)
            client_socket.send(new_token.encode('utf-8'))
        else:
            client_socket.send('False'.encode('utf-8'))
    
    for client in clients:
        print(client, clients[client])

    client_socket.close()

def generate_token():
    return str(uuid.uuid4())

def register_client(client_address, token, client_socket, hostname):
    clients[token] = {'hostname': hostname, 'address': client_address[0], 'socket': client_socket}
    db.update_db_with_new_client(token, hostname, client_address[0])

def update_client(client_address, token, client_socket, hostname):
    clients[token]['address'] = client_address[0]
    clients[token]['socket'] = client_socket
    clients[token]['hostname'] = hostname

def list_client():
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