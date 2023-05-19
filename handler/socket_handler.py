import socket
import threading
import uuid
import sqlite.db as db
import ssl
import json

clients = db.init_db()
server_running = True
server_socket = None

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
def start_server():
    global config
    global server_socket
    global server_running
    config = read_config()
    host = socket.gethostbyname(socket.gethostname())
    port = int(config["server_port"])

     # Crea un socket de servidor no seguro
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Envuelve el socket del servidor con SSL
    server_socket = ssl.wrap_socket(
        server_socket, 
        certfile='./certs/ca/ca.crt', 
        keyfile='./certs/ca/ca.key', 
        server_side=True
        )
    server_socket.bind((host, port))
    server_socket.settimeout(1)  # Establece un tiempo de espera de 1 segundo
    server_socket.listen()
    print(f"Servidor escuchando en {host}:{port}")

    while server_running:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client_init, args=(client_socket, client_address)).start()
        except socket.timeout:
            pass
    
    server_socket.close()

def stop_server():
    global server_running
    server_running = False
    
def handle_client_init(client_socket, client_address):
    received_data = client_socket.recv(1024).decode('utf-8')
    received_token, hostname = received_data.split('|')

    print (received_token, hostname)
    
    if received_token in clients and clients[received_token]['hostname'] == hostname:
        print ('token & hostname')
        update_client(client_address, received_token, client_socket, hostname)
        client_socket.send('True'.encode('utf-8'))
    else:
        value = True
        for index in clients.values():
            if index['hostname'] == hostname:
                value = False
        if value:
            new_client(hostname, client_address, client_socket)
        else:
            client_socket.send('False'.encode('utf-8'))

    for client in clients:
        print(client, clients[client])

    client_socket.close()

def generate_token():
    return str(uuid.uuid4())

def new_client(hostname, client_address, client_socket):
    new_token = generate_token()
    while new_token in clients:  # Asegurar que el token no se repita
        new_token = generate_token()
    register_client(client_address, new_token, client_socket, hostname)
    client_socket.send(new_token.encode('utf-8'))

def register_client(client_address, token, client_socket, hostname):
    clients[token] = {'hostname': hostname, 'address': client_address[0], 'socket': client_socket}
    db.register_db_with_new_client(token, hostname, client_address[0])

def update_client(client_address, token, client_socket, hostname):
    clients[token]['address'] = client_address[0]
    clients[token]['socket'] = client_socket
    db.update_client_address_in_db(hostname, client_address[0])

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
    
    checking_socket = init_client_connection(host)
    if checking_socket:
        checking_socket.send("validate_token".encode('utf-8'))
        response = checking_socket.recv(1024).decode('utf-8')
        if response == token:
            checking_socket.send("Validated".encode('utf-8'))
        else:
            checking_socket.send("NOT Validated".encode('utf-8'))
        checking_socket.close()
        return response == token
    else :
        return False

def init_client_connection(host):
    port = int(config["client_port"])
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       
        client_socket.settimeout(2)
        # Envuelve el socket del servidor con SSL
        client_socket = ssl.wrap_socket(
            client_socket,
            certfile='./certs/server/server.crt', 
            keyfile='./certs/server/server.key',
            ca_certs='./certs/ca/ca.crt',
            cert_reqs=ssl.CERT_REQUIRED
            )
        client_socket.connect((host, port))
        return client_socket
    except (socket.error, socket.timeout):
        return False