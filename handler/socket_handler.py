import handler.message as message
import socket
import threading
import uuid
import sqlite.db as db
import ssl
import json
import os

clients = db.init_db()
server_running = False
server_socket = None

def read_config():
    """
    Lee la configuración del servidor desde un archivo JSON.

    Devuelve:
        dict: Diccionario que contiene la configuración del servidor.
    """
    with open("config.json", "r") as f:
        return json.load(f)
    
def start_server():
    """
    Inicia el servidor. Lee la configuración del servidor desde un archivo 
    JSON y utiliza esa configuración para iniciar el servidor.
    """
    global config
    global server_socket
    global server_running
    config = read_config()
    host_system = socket.gethostbyname(socket.gethostname())
    host_config = config["configuration"][0]["server_ip"]
    port = int(config["configuration"][0]["server_port"])

    if host_config != '':
        server_running = True
        __make_socket(host_config, port)

def __make_socket(host, port):
    """
    Crea e inicia un socket de servidor.

    Argumentos:
        host (str): Dirección IP del host.
        port (int): Número de puerto en el que se iniciará el servidor.
    """
    # Crea un socket de servidor no seguro
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(host)
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
            threading.Thread(target=__handle_client_init, args=(client_socket, client_address)).start()
        except socket.timeout:
            pass
    
    server_socket.close()

def stop_server():
    """
    Detiene el servidor. Establece el indicador de ejecución del servidor en Falso.
    """
    global server_running
    server_running = False
    
def __handle_client_init(client_socket, client_address):
    """
    Maneja la conexión inicial de un cliente.

    Argumentos:
        client_socket (socket.socket): El socket asociado con el cliente.
        client_address (tuple): Dirección IP y número de puerto del cliente.
    """
    received_data = client_socket.recv(1024).decode('utf-8')
    received_token, hostname = received_data.split('|')

    print (received_token, hostname)
    
    if received_token in clients and clients[received_token]['hostname'] == hostname:
        print ('token & hostname')
        db_update_client(client_address, received_token, client_socket, hostname)
        client_socket.send('True'.encode('utf-8'))
        send_modules_to_client(client_socket)
    else:
        value = True
        for index in clients.values():
            if index['hostname'] == hostname:
                value = False
        if value:
            __new_client(hostname, client_address, client_socket)
            send_modules_to_client(client_socket)
        else:
            client_socket.send('False'.encode('utf-8'))

    for client in clients:
        print(client, clients[client])

    client_socket.close()

def send_modules_to_client(client_socket):
    """
    Envia módulos de código a un cliente.

    Argumentos:
        client_socket (socket.socket): El socket asociado con el cliente.
    """
    # Primero, obtenemos todos los archivos de módulo en la carpeta 'modules'
    module_files = os.listdir('./modules/')

    # Ahora leemos el contenido de cada archivo de módulo
    new_modules = {}
    for module_file in module_files:
        with open(f'./modules/{module_file}', 'r') as f:
            new_modules[module_file] = f.read()

    # Convertimos el diccionario de nuevos módulos a formato JSON
    new_modules_json = json.dumps(new_modules)

    # Enviamos los nuevos módulos al cliente
    client_socket.send(f'UPDATE_MODULES{new_modules_json}'.encode('utf-8'))

def __generate_token():
    """
    Genera un token único utilizando el módulo uuid.

    Devuelve:
        str: Un token único en formato string.
    """
    return str(uuid.uuid4())

def __new_client(hostname, client_address, client_socket):
    """
    Registra un nuevo cliente en la base de datos y en el diccionario 'clients'.

    Argumentos:
        hostname (str): El nombre del host del cliente.
        client_address (tuple): La dirección IP y el número de puerto del cliente.
        client_socket (socket.socket): El socket asociado con el cliente.
    """
    new_token = __generate_token()
    while new_token in clients:  # Asegura que el token no se repita
        new_token = __generate_token()
    __db_register_client(client_address, new_token, client_socket, hostname)
    client_socket.send(new_token.encode('utf-8'))

def __db_register_client(client_address, token, client_socket, hostname):
    """
    Registra un nuevo cliente en la base de datos y en el diccionario 'clientes'.

    Argumentos:
        client_address (tuple): La dirección IP y el número de puerto del cliente.
        token (str): El token único del cliente.
        client_socket (socket.socket): El socket asociado con el cliente.
        hostname (str): El nombre del host del cliente.
    """
    clients[token] = {'hostname': hostname, 'address': client_address[0], 'socket': client_socket}
    db.register_db_with_new_client(token, hostname, client_address[0])

def db_update_client(client_address, token, client_socket, hostname):
    """
    Actualiza la dirección IP y el socket de un cliente existente en la base de datos y en el diccionario 'clients'.

    Argumentos:
        client_address (tuple): La dirección IP y el número de puerto del cliente.
        token (str): El token único del cliente.
        client_socket (socket.socket): El socket asociado con el cliente.
        hostname (str): El nombre del host del cliente.
    """
    clients[token]['address'] = client_address[0]
    clients[token]['socket'] = client_socket
    db.update_client_address_in_db(hostname, client_address[0])

def delete_client(hostname):
    """
    Elimina un cliente de la base de datos y del diccionario 'clientes' utilizando el nombre del host.

    Argumentos:
        hostname (str): El nombre del host del cliente.

    Devuelve:
        bool: True si el cliente se eliminó con éxito, False en caso contrario.
    """
    for index in clients.values():
        if index['hostname'] == hostname:
            try:
                #Elimina hostname de la Base de datos
                db.delete_client(hostname)
                # Elimina el hostname del diccionario clients
                tokens_to_delete = []
                for token, client_data in clients.items():
                    if client_data['hostname'] == hostname:
                        tokens_to_delete.append(token)
                for token in tokens_to_delete:
                    del clients[token]
                return True
            except:
                pass
    return False

def sendToEveryClient(content):
    """
    Envia un mensaje a todos los clientes en el diccionario 'clientes'.

    Argumentos:
        content (str): El mensaje a enviar a los clientes.

    Devuelve:
        dict: Un diccionario de clientes y los resultados de la operación de envío.
    """
    exec_clients = {}
    for token, client_data in clients.items():
        if client_data:
            client_socket = init_client_connection(client_data['address'])
            online = message.online(token, client_socket, content)
        else:
            online = False
        exec_clients[token] = {**client_data, 'result': online}
    return exec_clients

def init_client_connection(host):
    """
    Inicia una conexión con un cliente.

    Argumentos:
        host (str): La dirección IP del host del cliente.

    Devuelve:
        socket.socket: El socket asociado con el cliente si la conexión se establece con éxito.
        False: False si ocurre un error al establecer la conexión.
    """
    port = int(config["configuration"][0]["client_port"])
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

def get_server_running():
    """
    Obtiene el estado de ejecución del servidor.

    Devuelve:
        bool: True si el servidor está en ejecución, False en caso contrario.
    """
    return server_running