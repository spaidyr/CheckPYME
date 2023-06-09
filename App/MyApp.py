from PyQt5.QtWidgets import QProgressDialog, QApplication, QMainWindow, QMenu, QMessageBox, QMenuBar, QAction, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
import handler.function as function
from App.ConfigWindow import ConfigWindow
from App.CertificatesConfigWindow import CertificatesConfigWindow
from App.InstallDialog import InstallDialog
from App.CertificatesAlert import CertificatesAlert
from App.PasswordDialog import PasswordDialog
from App.CreateUserWindow import CreateUserWindow
from App.PacketWindow import PacketWindow
from handler.Installer.elk_install import main as elk_install
import time


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        time.sleep(1)

        self.server_thread = function.get_server_running()
        self.tableWidget = QTableWidget()
        self.timer_clients_online = QTimer()
        self.timer_last_update = QTimer()
        self.last_mod_times = function.get_mod_times()
        self.initUI()

    def initUI(self):

        self.setWindowTitle("CheckPYME")  # Set the window title
        self.setGeometry(100, 100, 800, 600) # Establece la ventana en la posición (100, 100) y con tamaño 800px de ancho y 600px de alto
        
        menubar = self.menuBar()

        optionsMenu = QMenu('Options Menu', self)
        agentMenu = QMenu('Agent Management', self)
        elkMenu = QMenu('Elasticsearch', self)

        optionsMenu.addAction('List connected clients', self.list_clients)
        optionsMenu.addAction('Configuration', self.open_config)
        optionsMenu.addAction('Configuare Certificates', self.config_certs)
        optionsMenu.addAction('Genearte Packet_Client', self.generate_packetClient)
        optionsMenu.addAction('Quit', self.quit)

        agentMenu.addAction('Execute Modules', self.execute_modules)
        agentMenu.addAction('Update agents', self.update_agents)
        agentMenu.addAction('Delete agent', self.delete_agent)

        elkMenu.addAction('Start Elasticsearch', self.start_elasticsearch)
        elkMenu.addAction('Start Kibana', self.start_kibana)
        elkMenu.addAction('Check Index', self.check_index)
        elkMenu.addAction('Configure Elasticsearch password', self.elasticsearch_password)
        elkMenu.addAction('Configure Kibana System password', self.kibana_password)
        elkMenu.addAction('Create User for client', self.create_user)

        menubar.addMenu(optionsMenu)
        menubar.addMenu(agentMenu)
        menubar.addMenu(elkMenu)

        # Configure table widget
        self.tableWidget.setColumnCount(5) # 4 columns for Hostname, IP_Address, Online and Updated
        self.tableWidget.setHorizontalHeaderLabels(['Hostname', 'IP_Address', 'Online', 'last_check', 'last_update'])

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        time.sleep(1)

        if not self.server_thread:
            QMessageBox.warning(self, 'Server Error', 'Please configure the server IP.')
        else:
            #Inicialización elasticsearch
            dialog = InstallDialog(self)
            dialog.show()
            QApplication.processEvents()
            elk_install(dialog)
            #╗Comprobar si los certificados están creados
            check_ca , check_client, check_server = function.check_certificates()
            if not check_ca & check_client & check_server:
                alert = CertificatesAlert()
                alert.exec_()
            # Inicialización de tabla de clientes
            elif check_ca & check_client & check_server:

                #function.sart_server()
                self.list_clients()

                # Set a timer to update the table every 30 seconds
                self.timer_clients_online.timeout.connect(self.list_clients)
                self.timer_clients_online.start(30000) # 30000 ms = 30 seconds

                # Set a timer to update the table every 30 seconds
                self.timer_last_update.timeout.connect(self.update_agents)
                self.timer_last_update.start(30000) # 30000 ms = 30 seconds

    def list_clients(self):

        # Function to list clients
        result = function.list_clients()
        for token, client_data in result.items():
            print (result)
            online_status = QIcon("./App/icons/online.png") if client_data['result'] else QIcon("./App/icons/offline.png")
            
            # Find row by IP
            row = self.get_row_by_ip(client_data['address'])

            # If row doesn't exist, add a new row
            if row is None:
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(client_data['hostname']))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(client_data['address']))
            
            # Create a QTableWidgetItem
            item = QTableWidgetItem()
            # Create a QIcon
            icon = QIcon(QPixmap('./App/icons/online.png' if client_data['result'] else './App/icons/offline.png'))
            # Set the icon to the QTableWidgetItem
            item.setIcon(icon)
            # Align the icon to center
            item.setTextAlignment(Qt.AlignCenter)
            # Add the QTableWidgetItem to the table
            self.tableWidget.setItem(row, 2, item)

    def open_config(self):
        self.configWindow = ConfigWindow(self)
        self.configWindow.show()

    def config_certs(self):
        self.certsConfigWindow = CertificatesConfigWindow(self)
        self.certsConfigWindow.show()

    def execute_modules(self):

        # Function to execute modules
        result = function.excute_modules()
        for token, client_data in result.items():
            if client_data['result']:  # if the result is True
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get current date and time
                row = self.get_row_by_hostname(client_data['hostname'])  # find the row of the agent by hostname
                if row is not None:
                    self.tableWidget.setItem(row, 3, QTableWidgetItem(current_datetime))  # update the 'last_check' cell

    def update_agents(self):

        check_mod_times = function.get_mod_times()

        if check_mod_times == self.last_mod_times:
            pass
        else:
            # Function to update agents
            result = function.update_clients()
            for token, client_data in result.items():
                if client_data['result']:  # if the result is True
                    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get current date and time
                    row = self.get_row_by_hostname(client_data['hostname'])  # find the row of the agent by hostname
                    if row is not None:
                        self.tableWidget.setItem(row, 4, QTableWidgetItem(current_datetime))  # update the 'last_check' cell

    def get_row_by_hostname(self, hostname):
        # Loop over all rows
        for row in range(self.tableWidget.rowCount()):
            # If the hostname in the row matches the given hostname
            if self.tableWidget.item(row, 0).text() == hostname:
                return row
        # Return None if no matching hostname is found
        return None

    def get_row_by_ip(self, ip):
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 1).text() == ip:
                return row
        return None

    def delete_agent(self):
        # Show input dialog to get the hostname
        hostname, ok = QInputDialog.getText(self, 'Delete Agent', 'Enter the hostname:')
        if ok:
            # Function to delete agent
            result = function.delete_client(hostname)
            if result:
                QMessageBox.information(self, 'Delete Agent', 'Agent deleted')
                # Remove the agent from the table
                row = self.get_row_by_hostname(hostname)
                if row is not None:
                    self.tableWidget.removeRow(row)
            else:
                QMessageBox.information(self, 'Delete Agent', 'Error')
        self.list_clients()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to shut down the server?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            function.stop_server()
            event.accept()  # accept the event
        else:
            event.ignore()  # ignore the event

    def elasticsearch_password(self):
        try:
            function.reset_elasticsearch_password()
        except:
            print("Error, you should first configure Elasticsearch before executing this action")

    def kibana_password(self):
        try:
            function.reset_kibana_password()
            msgBox = PasswordDialog()
            msgBox.exec()
        except:
            print("Error, you should first configure Elasticsearch before executing this action")

    def start_elasticsearch(self):
        function.start_elasticsearch()

    def start_kibana(self):
        function.start_kibana()

    def check_index(self):
        result = function.check_and_create_index()
        if result == "Connection failed":
            QMessageBox.critical(self, 'Error', result)
        elif result == "Índice creado con éxito.":
            QMessageBox.information(self, 'Exito', result)
        elif result == "El índice ya existe.":
            QMessageBox.information(self, 'Información', result)

    def create_user(self):
        self.createUserWindow = CreateUserWindow()
        self.createUserWindow.show()
    
    def generate_packetClient(self):
        self.window = PacketWindow()
        self.window.show()

    def quit(self):
        # Function to quit
        reply = QMessageBox.question(self, 'Menssage', 'Are you sure you want to shut down the server? (y/n): ', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            function.stop_server()
            QApplication.instance().quit()
