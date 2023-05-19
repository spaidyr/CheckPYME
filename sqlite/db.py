import sqlite3

def init_db():
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
    cur = conn.cursor()
    cur.execute("SELECT token, hostname FROM agents")
    clients = {}

    for row in cur.fetchall():
        token, hostname = row
        clients[token] = {'hostname': hostname}
    
    return clients

def load_client_addresses(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientAddress")
    addresses = cursor.fetchall()
    return addresses

def register_db_with_new_client(token, hostname, address):
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agents (token, hostname) VALUES (?, ?)", (token, hostname))
    cursor.execute("INSERT INTO clientAddress (hostname, address) VALUES (?, ?)", (hostname, address))
    conn.commit()
    conn.close()

def update_client_address_in_db(hostname, new_address):
    conn = sqlite3.connect('sqlite/CheckPYME.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE clientAddress SET address = ? WHERE hostname = ?", (new_address, hostname))

    conn.commit()
    conn.close()

