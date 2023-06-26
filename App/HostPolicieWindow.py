from PyQt5.QtWidgets import QVBoxLayout, QGridLayout, QDialog, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from handler.function import get_config as get_config
from handler.function import get_status_policie as get_value
from handler.function import get_booleans_security as get_booleans
from App.DetailedWindow import DetailedWindow

class HostPolicieWindow(QDialog):
    """
    Clase para crear una ventana de diálogo que muestra el estado de las políticas para un host específico.

    Atributos:
    hostname (str): Nombre del host para el que se mostrarán las políticas.
    table (QTableWidget): Tabla que muestra las políticas y su estado.
    """
    def __init__(self, hostname):
        """
        Constructor de la clase HostPolicieWindow.

        Parámetros:
        hostname (str): Nombre del host para el que se mostrarán las políticas.
        """
        super().__init__()
        self.hostname = hostname
        self.__initUI()

    def __initUI(self):
        """
        Inicializa la interfaz de usuario para la ventana de diálogo. Esta interfaz consiste en una tabla
        que muestra los módulos y su estado para el host seleccionado y una serie de etiquetas y widgets
        que muestran información adicional sobre los niveles de seguridad.
    
        La tabla se llena con los datos de los módulos obtenidos del archivo de configuración. Cada fila
        de la tabla representa un módulo y tiene dos columnas: el nombre del módulo y su estado. El estado
        del módulo se colorea de acuerdo a su nivel de cumplimiento, usando rojo para 'Ninguno', naranja
        para 'bajo', amarillo para 'medio' y verde para 'alto'.
    
        Por debajo de la tabla, se muestra información adicional sobre el cumplimiento de los niveles de
        seguridad en forma de porcentajes. Esto se presenta en tres columnas para los niveles 'bajo',
        'medio' y 'alto', respectivamente. Los porcentajes se calculan utilizando la función
        'get_true_percentage' y representan la proporción de elementos con valor 'True' para cada nivel
        de seguridad.
    
        Por último, la función conecta la señal 'cellClicked' de la tabla a la función 'open_detailed_window',
        que abre una nueva ventana con información detallada sobre el módulo seleccionado.
        """
        self.setWindowTitle(self.hostname)

        vbox = QVBoxLayout()

        config = get_config()
        modules = config['modules']

        # Crea una tabla con tantas filas como módulos y 2 columnas
        self.table = QTableWidget(len(modules[0]), 2)

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
        for module in modules:
            for i, (key, value) in enumerate(module.items()):
                try: 
                    value = get_value(key, self.hostname)
                except:
                    value = ""

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
        
        self.table.cellClicked.connect(self.__open_detailed_window)

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

        percent_low = QLabel(f"{self.__get_true_percentage(booleans_low):.2f}%")
        percent_medium = QLabel(f"{self.__get_true_percentage(booleans_medium):.2f}%")
        percent_high = QLabel(f"{self.__get_true_percentage(booleans_high):.2f}%")

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

    def __get_true_percentage(self, count_dict):
        """
        Calcula el porcentaje de elementos con valor True en el diccionario proporcionado.

        Parámetros:
        count_dict (dict): Diccionario con valores booleanos.

        Retorna:
        float: Porcentaje de elementos con valor True.
        """
        total = sum(count_dict.values())
        true_count = count_dict.get(True, 0)
        true_percentage = (true_count / total) * 100
        return true_percentage

    def __open_detailed_window(self, row, column):
        """
        Abre una nueva ventana detallada para el módulo seleccionado.

        Parámetros:
        row (int): Número de fila de la celda seleccionada.
        column (int): Número de columna de la celda seleccionada.
        """
        if column == 1:  # Si se ha hecho clic en la columna de "Status"
            module_item = self.table.item(row, 0)
            module_key = module_item.text() if module_item else ''
            value = self.table.item(row, 1)
            if value.text():
                detailed_window = DetailedWindow(self.hostname, module_key)
                detailed_window.exec_()