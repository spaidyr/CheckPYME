import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
from handler.function import generate_certificates, copy_file as copy_cert
import re

class CertificatesConfigWindow(QMainWindow):
    """
    Clase que implementa una ventana de configuración de certificados.

    Attributes
    ----------
    config : dict
        Diccionario para almacenar la configuración de los certificados leída del archivo de configuración.
    layout : QVBoxLayout
        Layout principal para la ventana de configuración de certificados.
    tables : list
        Lista para almacenar referencias a las tablas que contienen la configuración de los certificados.
    """
    def __init__(self, parent=None):
        """
        Constructor de la clase. Inicializa la interfaz de usuario y carga la configuración de los certificados desde el archivo de configuración.
        """
        super(CertificatesConfigWindow, self).__init__(parent)

        # Load config
        with open('./certs/config.json') as f:
            self.config = json.load(f)

        # Set window title and size
        self.setWindowTitle("Configure Certificates")
        self.setGeometry(1000, 100, 320, 820)

        # Create layout
        self.layout = QVBoxLayout()

        # Create a table for each certificate type
        self.tables = []  # keep track of tables for saving later
        for cert_type in ['ca', 'client', 'server']:
            self.layout.addWidget(QLabel(cert_type.upper()))
            table = self.create_table(self.config[cert_type])
            self.tables.append((cert_type, table))  # add table to tables list
            self.layout.addWidget(table)

        # Create save button
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_config)
        self.layout.addWidget(save_button)

        # Set layout
        centralWidget = QWidget()
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)

    def create_table(self, config):
        """
        Crea una tabla QTableWidget para mostrar las claves y valores de una configuración de certificados.
        La tabla tiene tantas filas como elementos en la configuración y dos columnas para 'Key' y 'Value'. 
        Para cada clave y valor en la configuración, se crea un QTableWidgetItem para la clave y un QLineEdit para el valor.

        Parameters
        ----------
        config : dict
            Diccionario que contiene la configuración de los certificados.

        Returns
        -------
        table : QTableWidget
            Tabla que contiene los widgets para la visualización y edición de la configuración de los certificados.
        """
        table = QTableWidget()
        table.setRowCount(len(config))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Key', 'Value'])

        for i, (key, value) in enumerate(config.items()):
            table.setItem(i, 0, QTableWidgetItem(key))
            if isinstance(value, str) and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
                lineEdit = QLineEdit(value)
            else:
                lineEdit = QLineEdit(str(value))
            table.setCellWidget(i, 1, lineEdit)

        table.resizeColumnsToContents()

        return table

    def save_config(self):
        """
        Guarda la configuración en el archivo 'config.json'. Recoge los valores de las celdas de las tablas y los guarda en el diccionario 
        de configuración. Luego vuelca el diccionario en el archivo de configuración. Después de guardar la configuración, muestra un cuadro 
        de mensaje preguntando al usuario si desea generar nuevos certificados. Si el usuario acepta, se llaman a las funciones 
        'generate_certificates' y 'copy_cert' para generar y copiar los certificados, respectivamente.
        """
        for cert_type, table in self.tables:  # iterate over each table
            config = {table.item(row, 0).text(): table.cellWidget(row, 1).text() for row in range(table.rowCount())}
            self.config[cert_type] = config

        with open('./certs/config.json', 'w') as f:
            json.dump(self.config, f)

        reply = QMessageBox.question(self, 'Generate Certificates', 
            "Would you like to generate new certificates?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            generate_certificates()
            copy_cert("./certs/ca/ca.crt", "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\config\ca.crt")
            copy_cert("./certs/ca/ca.crt", "C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\ca.crt")
            copy_cert("./certs/server/server.crt", "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\config\server.crt")
            copy_cert("./certs/server/server.crt", "C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\server.crt")
            copy_cert("./certs/server/server.key", "C:\\Elastic\\Elasticsearch\\8.8.0\\elasticsearch-8.8.0\\config\server.key")
            copy_cert("./certs/server/server.key", "C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\server.key")

        self.close()
