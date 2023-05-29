import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
from handler.function import generate_certificates

class CertificatesConfigWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CertificatesConfigWindow, self).__init__(parent)

        # Load config
        with open('./certs/config.json') as f:
            self.config = json.load(f)

        # Set window title and size
        self.setWindowTitle("Configure Certificates")
        self.setGeometry(1000, 100, 320, 750)

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
        table = QTableWidget()
        table.setRowCount(len(config))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Key', 'Value'])

        for i, (key, value) in enumerate(config.items()):
            table.setItem(i, 0, QTableWidgetItem(key))
            lineEdit = QLineEdit(str(value))
            table.setCellWidget(i, 1, lineEdit)

        table.resizeColumnsToContents()

        return table

    def save_config(self):
        for cert_type, table in self.tables:  # iterate over each table
            config = {table.item(row, 0).text(): table.cellWidget(row, 1).text() for row in range(table.rowCount())}
            self.config[cert_type] = config

        with open('./certs/config.json', 'w') as f:
            json.dump(self.config, f)

        reply = QMessageBox.question(self, 'Generate Certificates', 
            "Would you like to generate new certificates?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            generate_certificates()

        self.close()
