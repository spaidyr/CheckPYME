from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QTableWidget, QTableWidgetItem, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from handler.function import get_policie as get_policie
from handler.function import get_booleans_policie as get_booleans

class DetailedWindow(QDialog):
    def __init__(self, hostname, module_key):
        super().__init__()
        self.hostname = hostname
        self.module_key = module_key
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'{self.module_key} on {self.hostname}')
        self.setGeometry(1100, 100, 307, 400)

        vbox = QVBoxLayout()
        policies = get_policie(self.hostname, self.module_key)

        # Crea una tabla con tantas filas como elementos en "policies" y 2 columnas
        table = QTableWidget(len(policies), 2)

        # Establece los encabezados de las columnas
        table.setHorizontalHeaderLabels(["Policy", "Status"])
        table.setColumnWidth(0,150)

        colors = {
            'None': QColor('red'),
            'low': QColor('orange'),
            'medium': QColor('yellow'),
            'high': QColor('green'),
        }

        # Rellena la tabla con los datos de las políticas
        for i, (key, value) in enumerate(policies.items()):
            # Añade la clave y el valor a la fila correspondiente
            key_item = QTableWidgetItem(key)
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)  # make the cell read-only
            value_item = QTableWidgetItem(value)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)  # make the cell read-only

            # Alinea el texto al centro
            value_item.setTextAlignment(Qt.AlignCenter)

            # Colorea la celda de estado si el valor está en el diccionario de colores
            if value in colors:
                value_item.setBackground(colors[value])
            
            table.setItem(i, 0, key_item)
            table.setItem(i, 1, value_item)

        vbox.addWidget(table)

        # Crea el layout para las tres columnas y dos filas
        grid_Title = QGridLayout()
        grid_layout = QGridLayout()

        # Agrega etiquetas con los nombres en la primera fila
        label1 = QLabel("LOW")
        label2 = QLabel("MEDIUM")
        label3 = QLabel("HIGH")
        texto = QLabel("Porcentaje de Cumplimiento con los\nniveles de seguridad de las Guias STIC")

        booleans_low = get_booleans(self.hostname, self.module_key, security_level="low")
        booleans_medium = get_booleans(self.hostname, self.module_key, security_level="medium")
        booleans_high = get_booleans(self.hostname, self.module_key, security_level="high")

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