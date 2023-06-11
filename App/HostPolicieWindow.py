from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QDialog, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from handler.function import read_config as read_config
from handler.function import get_status_policie as get_value
from handler.function import get_booleans_security as get_booleans
from App.DetailedWindow import DetailedWindow

class HostPolicieWindow(QDialog):
    
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.hostname)

        vbox = QVBoxLayout()

        config = read_config()
        modules = config['modules']

        # Crea una tabla con tantas filas como módulos y 2 columnas
        self.table = QTableWidget(len(modules), 2)

        # Establece los encabezados de las columnas
        self.table.setHorizontalHeaderLabels(["Module", "Status"])

        # Colores para los niveles de cumplimiento
        colors = {
            'None': QColor('red'),
            'low': QColor('orange'),
            'medium': QColor('yellow'),
            'high': QColor('green'),
        }

        # Rellena la tabla con los datos de los módulos
        for i, module in enumerate(modules):
            for key, value in module.items():
                value = get_value(key, self.hostname)

                # Añade el nombre del módulo y su estado a la fila correspondiente
                module_item = QTableWidgetItem(key)
                module_item.setFlags(module_item.flags() & ~Qt.ItemIsEditable)  # make the cell read-only
                status_item = QTableWidgetItem(value)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)  # make the cell read-only

                # Alinea el texto al centro
                status_item.setTextAlignment(Qt.AlignCenter)
                
                # Colorea la celda de estado si el valor está en el diccionario de colores
                if value in colors:
                    status_item.setBackground(colors[value])
                
                self.table.setItem(i, 0, module_item)
                self.table.setItem(i, 1, status_item)
        
        self.table.cellClicked.connect(self.open_detailed_window)

        # Añade la tabla al layout
        vbox.addWidget(self.table)

        # Conecta la señal cellClicked de la tabla a la función que abre la ventana detallada

        # Crea el layout para las tres columnas y dos filas
        grid_Title = QGridLayout()
        grid_layout = QGridLayout()

        # Agrega etiquetas con los nombres en la primera fila
        label1 = QLabel("LOW")
        label2 = QLabel("MEDIUM")
        label3 = QLabel("HIGH")
        texto = QLabel("Porcentaje de Cumplimiento con los\nniveles de seguridad de las Guias STIC")

        booleans_low = get_booleans(self.hostname, security_level="low")
        booleans_medium = get_booleans(self.hostname, security_level="medium")
        booleans_high = get_booleans(self.hostname, security_level="high")

        percent_low = QLabel(f"{self.get_true_percentage(booleans_low):.2f}%")
        percent_medium = QLabel(f"{self.get_true_percentage(booleans_medium):.2f}%")
        percent_high = QLabel(f"{self.get_true_percentage(booleans_high):.2f}%")

        # Agrega widgets a las celdas del layout
        grid_Title.addWidget(texto, 0, 0)
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(label2, 0, 1)
        grid_layout.addWidget(label3, 0, 2)
        grid_layout.addWidget(percent_low, 1, 0)
        grid_layout.addWidget(percent_medium, 1, 1)
        grid_layout.addWidget(percent_high, 1, 2)  

        grid_Title.setAlignment(Qt.AlignCenter)

        # Agrega el grid layout al layout principal
        vbox.addLayout(grid_Title)
        vbox.addLayout(grid_layout)

        self.setLayout(vbox)

    def get_true_percentage(self, count_dict):
        total = sum(count_dict.values())
        true_count = count_dict.get(True, 0)
        true_percentage = (true_count / total) * 100
        return true_percentage

    def open_detailed_window(self, row, column):
        if column == 1:  # Si se ha hecho clic en la columna de "Status"
            module_item = self.table.item(row, 0)
            module_key = module_item.text() if module_item else ''
            detailed_window = DetailedWindow(self.hostname, module_key)
            detailed_window.exec_()