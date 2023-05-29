import handler.socket_handler as socket_handler
import certs.certs as certs
from PyQt5.QtWidgets import QApplication
from App.MyApp import MyApp
from App.CertificatesAlert import CertificatesAlert
import threading
import os
import sys

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

def run_app():
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

def main():
    
    app = QApplication(sys.argv)
    
    check_ca , check_client, check_server = check_certificates()

    if not check_ca & check_client & check_server:
        alert = CertificatesAlert()
        alert.exec_()
    else:
        server_thread = threading.Thread(target=socket_handler.start_server).start()
    
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
