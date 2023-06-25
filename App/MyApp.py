"""
Importación de bibliotecas y módulos necesarios
"""
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
from datetime import datetime
import handler.function as function
from handler.Installer.elk_install import main as elk_install
from App.ConfigWindow import ConfigWindow
from App.CertificatesConfigWindow import CertificatesConfigWindow
from App.InstallDialog import InstallDialog
from App.CertificatesAlert import CertificatesAlert
from App.PasswordDialog import PasswordDialog
from App.CreateUserWindow import CreateUserWindow
from App.PacketWindow import PacketWindow
from App.HostPolicieWindow import HostPolicieWindow


class MyApp(QMainWindow):
    """
    Esta es la clase principal que inicia y controla la interfaz gráfica de la aplicación.
    
    Atributos:
        server_thread: Un objeto de hilo que representa el servidor en ejecución.
        tableWidget: Un objeto QTableWidget para mostrar datos en una estructura tabular.
        timer_clients_online: Un objeto QTimer para manejar el tiempo de los clientes en línea.
        timer_last_update: Un objeto QTimer para manejar el tiempo desde la última actualización.
        last_mod_times: Un objeto que almacena los tiempos de modificación.

    Métodos:
        initUI(): Este método inicializa la interfaz de usuario.
        closeEvent(event): Este método maneja el evento de cierre de la aplicación.
        color_compliance_cells(): Este método colorea las celdas de la columna 'Compliance STICS'.
        open_host_policie_window(row, column): Este método abre la ventana de políticas del host cuando se hace clic en una celda.
        quit(): Este método cierra la aplicación.
    """

    """
    Clase principal que inicia y controla la interfaz gráfica de la aplicación.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(MyApp, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        """
        Constructor para la clase MyApp.
        
        Inicializa la aplicación, crea los widgets necesarios y establece los temporizadores y las variables necesarias.
        """
        super().__init__()

        time.sleep(1)

        self.server_thread = function.get_server_running()
        self.tableWidget = QTableWidget()
        self.timer_clients_online = QTimer()
        self.timer_last_update = QTimer()
        self.last_mod_times = function.get_mod_times()
        
        self.initUI()

    def initUI(self):
        """
        Inicializa la interfaz de usuario.
        
        Este método configura el título y la geometría de la ventana principal, crea e inicializa los widgets y 
        los agrega a la ventana principal. También se conectan las señales y los slots para manejar los eventos de usuario.
        """
        self.setWindowTitle("CheckPYME")  # Set the window title
        self.setGeometry(100, 100, 865, 600) # Establece la ventana en la posición (100, 100) y con tamaño 800px de ancho y 600px de alto
        
        menubar = self.menuBar()

        optionsMenu = QMenu('Options Menu', self)
        agentMenu = QMenu('Agent Management', self)
        elkMenu = QMenu('Elasticsearch', self)

        optionsMenu.addAction('List connected clients', self.__thread_clients)
        optionsMenu.addAction('Configuration', self.__open_config)
        optionsMenu.addAction('Configuare Certificates', self.__config_certs)
        optionsMenu.addAction('Genearte Packet_Client', self.__generate_packetClient)
        optionsMenu.addAction('Quit', self.quit)

        agentMenu.addAction('Execute Modules', self.__execute_modules)
        agentMenu.addAction('Update agents', self.__update_agents)
        agentMenu.addAction('Delete agent', self.__delete_agent)
        agentMenu.addAction('Check STICS and Guides', self.__thread_full_security)
        agentMenu.addAction('Check security with custom policies', self.__thread_custom_security)

        elkMenu.addAction('Start Elasticsearch', self.__start_elasticsearch)
        elkMenu.addAction('Start Kibana', self.__start_kibana)
        elkMenu.addAction('Check Index', self.__check_index)
        elkMenu.addAction('Configure Elasticsearch password', self.__elasticsearch_password)
        elkMenu.addAction('Configure Kibana System password', self.__kibana_password)
        elkMenu.addAction('Create User for client', self.__create_user)

        menubar.addMenu(optionsMenu)
        menubar.addMenu(agentMenu)
        menubar.addMenu(elkMenu)

        # Configure table widget
        self.tableWidget.setColumnCount(7) # 7 columns for Hostname, IP_Address, Online and Updated
        self.tableWidget.setHorizontalHeaderLabels(['Hostname', 'IP_Address', 'Online', 'last_check', 'last_update', 'Compliance STIC', 'Compliance Custom'])
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(2, 50)
        self.tableWidget.setColumnWidth(3, 115)
        self.tableWidget.setColumnWidth(4, 115)
        self.tableWidget.setColumnWidth(5, 150)
        self.tableWidget.setColumnWidth(6, 150)


        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        time.sleep(1)

        server_ip = function.get_server_ip()

        if not server_ip:
            QMessageBox.warning(self, 'Server Error', 'Please configure the server IP.')
        else:
            #Inicialización elasticsearch
            dialog = InstallDialog(self)
            dialog.show()
            QApplication.processEvents()
            elk_install(dialog)

            #Comprobar si los certificados están creados
            check_ca , check_client, check_server = function.check_certificates()
            if not check_ca & check_client & check_server:
                alert = CertificatesAlert()
                alert.exec_()
            
            # Inicialización de tabla de clientes
            elif check_ca & check_client & check_server:

                function.sart_server()

                count = 0
                while not self.server_thread:
                    time.sleep(1)
                    self.server_thread = function.get_server_running()
                    count =+ 1
                    if count == 20:
                        break
                #function.sart_server()
                self.__thread_clients()
                time.sleep(1)


                # Set a timer to update the table every 30 seconds
                self.timer_clients_online.timeout.connect(self.__thread_clients)
                self.timer_clients_online.start(30000) # 30000 ms = 30 seconds

                # Set a timer to update the table every 30 seconds
                self.timer_last_update.timeout.connect(self.__update_agents)
                self.timer_last_update.start(30000) # 30000 ms = 30 seconds



    def __thread_clients(self):
        """
        Inicia un nuevo hilo para listar los clientes.

        Este método crea e inicia un nuevo hilo que llama a la función list_clients() de la clase.
        """
        list_clients_thread = threading.Thread(target=self.__list_clients).start()

    def __thread_full_security(self):
        """
        Inicia un nuevo hilo para verificar la seguridad completa y luego colorea las celdas de cumplimiento.

        Este método crea e inicia un nuevo hilo que llama a la función check_full_security() de la clase, 
        espera durante tres segundos, y luego llama a la función color_compliance_cells() para colorear las celdas de cumplimiento.
        """
        check_security_thread = threading.Thread(target=self.__check_full_security).start()
        time.sleep(3)
        self.__color_compliance_cells()
        
    
    def __thread_custom_security(self):
        """
        Inicia un nuevo hilo para verificar la seguridad personalizada y luego colorea las celdas de cumplimiento.

        Este método crea e inicia un nuevo hilo que llama a la función check_custom_security() de la clase, 
        espera durante tres segundos, y luego llama a la función color_compliance_cells() para colorear las celdas de cumplimiento.
        """
        check_security_thread = threading.Thread(target=self.__check_custom_security).start()
        time.sleep(3)
        self.__color_compliance_cells()
    
    def __list_clients(self):
        """
        Lista los clientes y actualiza la tabla en la interfaz de usuario.

        Este método llama a la función list_clients() de una clase externa para obtener 
        los datos de los clientes, luego actualiza la tabla en la interfaz de usuario con 
        los datos de los clientes, incluyendo el estado en línea o fuera de línea de cada cliente.
        """

        # Function to list clients
        result = function.get_list_clients()
        for token, client_data in result.items():
#            online_status = QIcon(QPixmap("./App/icons/online.png") if client_data['result'] else QIcon(QPixmap("./App/icons/offline.png")))
            
            # Find row by IP
            row = self.__get_row_by_ip(client_data['address'])

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
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            # Align the icon to center
            item.setTextAlignment(Qt.AlignCenter)
            # Add the QTableWidgetItem to the table
            self.tableWidget.setItem(row, 2, item)
            
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def __check_full_security(self):
        """
        Verifica la seguridad completa.

        Este método llama a la función check_security() de una clase externa con el 
        parámetro 'full' para verificar la seguridad completa.
        """
        function.check_security(parameter='full')
    
    def __check_custom_security(self):
        """
        Verifica la seguridad personalizada.

        Este método llama a la función check_security() de una clase externa con el 
        parámetro 'custom' para verificar la seguridad personalizada.
        """
        function.check_security(parameter='custom')

    def __open_config(self):
        """
        Abre la ventana de configuración.

        Este método crea e muestra una nueva ventana de configuración.
        """
        self.configWindow = ConfigWindow(self)
        self.configWindow.show()

    def __config_certs(self):
        """
        Abre la ventana de configuración de certificados.

        Este método crea y muestra una nueva ventana de configuración de certificados.
        """
        self.certsConfigWindow = CertificatesConfigWindow(self)
        self.certsConfigWindow.show()

    def __execute_modules(self):
        """
        Ejecuta los módulos y actualiza la tabla en la interfaz de usuario.

        Este método llama a la función execute_modules() de una clase externa para 
        ejecutar los módulos, luego actualiza la columna 'last_check' en la tabla de 
        la interfaz de usuario con la fecha y hora actuales para cada agente que tuvo 
        un resultado exitoso.
        """
        # Function to execute modules
        result = function.excute_modules()
        for token, client_data in result.items():
            if client_data['result']:  # if the result is True
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get current date and time
                row = self.__get_row_by_hostname(client_data['hostname'])  # find the row of the agent by hostname
                if row is not None:
                    self.tableWidget.setItem(row, 3, QTableWidgetItem(current_datetime))  # update the 'last_check' cell
        
        time.sleep(2)
        self.__check_full_security()

    def __update_agents(self):
        """
        Actualiza los agentes y actualiza la tabla en la interfaz de usuario.

        Este método llama a la función get_mod_times() de una clase externa para 
        obtener los tiempos de modificación, luego si los tiempos de modificación 
        son diferentes a los últimos tiempos de modificación almacenados, llama a 
        la función update_clients() de una clase externa para actualizar los clientes, 
        y finalmente actualiza la columna 'last_check' en la tabla de la interfaz 
        de usuario con la fecha y hora actuales para cada agente que tuvo un 
        resultado exitoso.
        """
        check_mod_times = function.get_mod_times()

        if check_mod_times == self.last_mod_times:
            pass
        else:
            # Function to update agents
            result = function.update_clients()
            for token, client_data in result.items():
                if client_data['result']:  # if the result is True
                    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get current date and time
                    row = self.__get_row_by_hostname(client_data['hostname'])  # find the row of the agent by hostname
                    if row is not None:
                        self.tableWidget.setItem(row, 4, QTableWidgetItem(current_datetime))  # update the 'last_check' cell

    def __get_row_by_hostname(self, hostname):
        """
        Devuelve el índice de la fila que corresponde al nombre de host dado.

        Args:
            hostname (str): El nombre de host para el que se busca la fila.

        Returns:
            int: El índice de la fila que corresponde al nombre de host, o None si no se encuentra ninguna fila que corresponda.
        """
        # Loop over all rows
        for row in range(self.tableWidget.rowCount()):
            # If the hostname in the row matches the given hostname
            if self.tableWidget.item(row, 0).text() == hostname:
                return row
        # Return None if no matching hostname is found
        return None

    def __get_row_by_ip(self, ip):
        """
        Devuelve el índice de la fila que corresponde a la IP dada.

        Args:
            ip (str): La IP para la cual se busca la fila.

        Returns:
            int: El índice de la fila que corresponde a la IP, o None si no se encuentra ninguna fila que corresponda.
        """
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 1).text() == ip:
                return row
        return None

    def __delete_agent(self):
        """
        Elimina un agente.

        Este método muestra un cuadro de diálogo de entrada para obtener el nombre 
        de host del agente a eliminar, luego llama a la función delete_client() de 
        una clase externa con el nombre de host dado para eliminar el agente, y 
        finalmente si el agente se eliminó con éxito, lo elimina de la tabla en 
        la interfaz de usuario y muestra un mensaje de información.
        """
        # Show input dialog to get the hostname
        hostname, ok = QInputDialog.getText(self, 'Delete Agent', 'Enter the hostname:')
        if ok:
            # Function to delete agent
            result = function.delete_client(hostname)
            if result:
                QMessageBox.information(self, 'Delete Agent', 'Agent deleted')
                # Remove the agent from the table
                row = self.__get_row_by_hostname(hostname)
                if row is not None:
                    self.tableWidget.removeRow(row)
            else:
                QMessageBox.information(self, 'Delete Agent', 'Error')
        self.__list_clients()

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la aplicación.
        
        Este método se llama cuando se cierra la ventana principal. Presenta un cuadro de diálogo 
        de confirmación y si el usuario confirma, detiene el servidor y cierra la aplicación.
        
        Parámetros:
            event (QCloseEvent): El evento de cierre.
        """
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to shut down the server?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            function.stop_server()
            event.accept()  # accept the event
        else:
            event.ignore()  # ignore the event

    def __elasticsearch_password(self):
        """
        Intenta resetear la contraseña de Elasticsearch.

        Este método llama a la función reset_elasticsearch_password() de una clase 
        externa para resetear la contraseña de Elasticsearch. 
        Si ocurre alguna excepción durante el proceso, se imprime un mensaje de error.
        """
    # ..
        try:
            function.reset_elasticsearch_password()
        except:
            print("Error, you should first configure Elasticsearch before executing this action")

    def __kibana_password(self):
        """
        Intenta resetear la contraseña de Kibana y muestra un cuadro de diálogo de contraseña.

        Este método llama a la función reset_kibana_password() de una clase externa para resetear la contraseña de Kibana. 
        Si se logra resetear la contraseña, se muestra un cuadro de diálogo de contraseña.
        Si ocurre alguna excepción durante el proceso, se imprime un mensaje de error.
        """
        try:
            function.reset_kibana_password()
            msgBox = PasswordDialog()
            msgBox.exec()
        except:
            print("Error, you should first configure Elasticsearch before executing this action")

    def __start_elasticsearch(self):
        """
        Inicia Elasticsearch.

        Este método llama a la función start_elasticsearch() de una clase externa para iniciar Elasticsearch.
        """
        function.start_elasticsearch()

    def __start_kibana(self):
        """
        Inicia Kibana.

        Este método llama a la función start_kibana() de una clase externa para iniciar Kibana.
        """
        function.start_kibana()

    def __check_index(self):
        """
        Verifica e intenta crear los índices en Elasticsearch.

        Este método llama a la función check_and_create_index() de una clase externa para verificar e intentar crear los índices en Elasticsearch, 
        luego muestra un mensaje en un cuadro de diálogo de acuerdo con el resultado de la verificación y la creación del índice.
        """
        results = function.check_and_create_index()
        if "Connection failed" in results:
            QMessageBox.critical(self, 'Error', "Connection failed")
        else:
            for result in results:
                if "creado con éxito" in result:
                    QMessageBox.information(self, 'Exito', result)
                elif "ya existe" in result:
                    QMessageBox.information(self, 'Información', result)

    def __create_user(self):
        """
        Abre la ventana de creación de usuario.

        Este método crea e muestra una nueva ventana de creación de usuario.
        """
        self.createUserWindow = CreateUserWindow()
        self.createUserWindow.show()
    
    def __generate_packetClient(self):
        """
        Abre la ventana de PacketWindow.

        Este método crea e muestra una nueva ventana de PacketWindow.
        """
        self.window = PacketWindow()
        self.window.show()
    
    def __color_compliance_cells(self):
        """
        Colorea las celdas de la columna 'Compliance STICS'.
        
        Este método colorea las celdas en la columna 'Compliance STICS' de la tabla en 
        función de los niveles de cumplimiento. Las celdas con un nivel alto de cumplimiento 
        se colorean de verde, las de nivel medio de amarillo y las de nivel bajo de rojo.
        """
        # Colores para los niveles de cumplimiento
        colors = {
            'None': QColor('red'),
            'low': QColor('orange'),
            'medium': QColor('yellow'),
            'high': QColor('green'),
        }

        # Fuente para el texto de las celdas
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)

        for row in range(self.tableWidget.rowCount()):
            # Obten el hostname de la fila actual
            hostname_item = self.tableWidget.item(row, 0)

            if hostname_item is None:
                continue  # si la celda está vacía, pasa a la siguiente fila

            hostname = hostname_item.text()
            # Obtiene el nivel de cumplimiento para el hostname actual
            level = function.get_compliance_full(hostname)

            # Si el nivel obtenido está en la lista de colores, colorea la celda
            if level in colors:
                item = QTableWidgetItem(level)
                item.setBackground(colors[level])  # set background color
                item.setForeground(QColor('black'))  # set text color
                item.setFont(font)  # set font
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 5, item)
            
            # Obtiene el nivel de cumplimiento custom para el hostname actual
            level_custom = function.get_compliance_custom(hostname)

            # Si el nivel obtenido está en la lista de colores, colorea la celda
            if level_custom in colors:
                item = QTableWidgetItem(level_custom)
                item.setBackground(colors[level_custom])  # set background color
                item.setForeground(QColor('black'))  # set text color
                item.setFont(font)  # set font
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 6, item)
            else:
                self.tableWidget.setItem(row, 6, None)
        self.tableWidget.cellClicked.connect(self.__open_host_policie_window)

    def __open_host_policie_window(self, row):
        """
        Abre la ventana de políticas del host cuando se hace clic en una celda.
        
        Este método se llama cuando se hace clic en una celda de la tabla. Abre una nueva 
        ventana que muestra las políticas del host para el host correspondiente a la fila de 
        la celda en la que se hizo clic.
        
        Parámetros:
            row (int): El índice de la fila en la que se hizo clic.
            column (int): El índice de la columna en la que se hizo clic.
        """
        hostname_item = self.tableWidget.item(row, 0)
        if hostname_item is None:
            return
        hostname = hostname_item.text()

        if hasattr(self, 'extraWindow'):  # Verifica si ya existe 'extraWindow'
            if isinstance(self.extraWindow, HostPolicieWindow):  # Verifica si 'extraWindow' es una instancia de 'HostPolicieWindow'
                self.extraWindow.close()  # Si es cierto, cierra la ventana existente

        self.extraWindow = HostPolicieWindow(hostname)
        self.extraWindow.show()

    def quit(self):
        """
        Cierra la aplicación.
        
        Este método detiene el servidor y cierra la aplicación. Se llama cuando se selecciona 
        la opción de salir en el menú de la aplicación o cuando se cierra la ventana principal.
        """
#        self.closeEvent(self.event)
        reply = QMessageBox.question(self, 'Menssage', 'Are you sure you want to shut down the server? (y/n): ', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            function.stop_server()
            QApplication.instance().quit()
    