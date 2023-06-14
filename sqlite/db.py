import sqlite3

def init_db():
    """
    Inicializa la base de datos SQLite, creando las tablas necesarias si no existen. 
    Carga los clientes y las direcciones de los clientes desde la base de datos.

    Retorna
    -------
    dict
        Un diccionario que contiene los clientes cargados desde la base de datos.
    """
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS agents
                    (token TEXT PRIMARY KEY NOT NULL,
                     hostname TEXT NOT NULL);''')
    conn.execute('''CREATE TABLE IF NOT EXISTS clientAddress (
                    hostname TEXT NOT NULL,
                    address TEXT NOT NULL,
                    FOREIGN KEY (hostname) REFERENCES agents (hostname));''')

    clients = load_clients_from_db(conn)
    addresses = load_client_addresses(conn)

    for address in addresses:
        hostname = address[0]
        ip = address[1]
        for token, client_data in clients.items():
            if client_data['hostname'] == hostname:
                clients[token]['address'] = ip
                break

    conn.close()
    return clients


def load_clients_from_db(conn):
    """
    Carga los clientes desde la base de datos.

    Parámetros
    ----------
    conn : sqlite3.Connection
        La conexión a la base de datos SQLite.

    Retorna
    -------
    dict
        Un diccionario que contiene los clientes cargados desde la base de datos.
    """
    cur = conn.cursor()
    cur.execute("SELECT token, hostname FROM agents")
    clients = {}

    for row in cur.fetchall():
        token, hostname = row
        clients[token] = {'hostname': hostname}
    
    return clients

def load_client_addresses(conn):
    """
    Carga las direcciones de los clientes desde la base de datos.

    Parámetros
    ----------
    conn : sqlite3.Connection
        La conexión a la base de datos SQLite.

    Retorna
    -------
    list
        Una lista de tuplas que contienen los hostnames y direcciones de los clientes.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientAddress")
    addresses = cursor.fetchall()
    return addresses

def register_db_with_new_client(token, hostname, address):
    """
    Registra un nuevo cliente en la base de datos.

    Parámetros
    ----------
    token : str
        El token del cliente.
    hostname : str
        El nombre del host del cliente.
    address : str
        La dirección IP del cliente.
    """
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agents (token, hostname) VALUES (?, ?)", (token, hostname))
    cursor.execute("INSERT INTO clientAddress (hostname, address) VALUES (?, ?)", (hostname, address))
    conn.commit()
    conn.close()

def update_client_address_in_db(hostname, new_address):
    """
    Actualiza la dirección IP de un cliente en la base de datos.

    Parámetros
    ----------
    hostname : str
        El nombre del host del cliente.
    new_address : str
        La nueva dirección IP del cliente.
    """
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE clientAddress SET address = ? WHERE hostname = ?", (new_address, hostname))

    conn.commit()
    conn.close()

def delete_client(hostname):
    """
    Elimina un cliente de la base de datos.

    Parámetros
    ----------
    hostname : str
        El nombre del host del cliente.
    """
    # Conéctate a la base de datos
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    cursor = conn.cursor()
    # Elimina el hostname de las tablas de la base de datos
    cursor.execute("DELETE FROM agents WHERE hostname = ?", (hostname,))
    cursor.execute("DELETE FROM clientAddress WHERE hostname = ?", (hostname,))

    # Commit y cierra la conexión
    conn.commit()
    conn.close()
