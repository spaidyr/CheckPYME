import handler.socket_handler as socket_handler
import certs.certs as certs
import cli
import threading
import os

def check_certificates():

    ca_certs = False
    client_certs = False
    server_certs = False

    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\ca\ca.key") or os.path.exists(".\certs\ca\ca.crt"):
        print("Los archivos de la CA ya existen.")
        ca_certs = True

    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\client\client.key") or os.path.exists("\.certs\client\client.crt"):
        print("Los archivos del cliente ya existen.")
        client_certs = True
    
    # Comprobar si los archivos ya existen
    if os.path.exists(".\certs\server\server.key") or os.path.exists("\.certs\server\server.crt"):
        print("Los archivos del cliente ya existen.")
        server_certs = True

    return ca_certs, client_certs, server_certs

def main():

    check_ca , check_client, check_server = check_certificates()

    if not check_ca & check_client & check_server:
        config = certs.read_config()
        ca_private_key, ca_cert = certs.generate_ca(config)
    
        if ca_private_key and ca_cert:
            client_private_key, client_cert = certs.generate_client_key_cert(ca_private_key, ca_cert, config)
            server_private_key, server_cert = certs.generate_server_key_cert(ca_private_key, ca_cert, config)

    server_thread = threading.Thread(target=socket_handler.start_server).start()

    cli_thread = threading.Thread(target=cli.main)
    cli_thread.start()

if __name__ == '__main__':
    main()
