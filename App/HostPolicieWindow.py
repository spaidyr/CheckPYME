from PyQt5.QtWidgets import QVBoxLayout, QGridLayout, QDialog, QTableWidget, QTableWidgetItem, QLabel, QSizePolicy
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
        self.config = None
        self.modules = None

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
        self.config = get_config()
        self.modules = self.config['modules']

        num_of_modules = len(self.modules[0])
        rows_per_column = 12
        
        # Calcula el número de columnas que necesitarás
        num_of_columns = (num_of_modules // rows_per_column) + (num_of_modules % rows_per_column > 0)
        
        self.table = QTableWidget(rows_per_column, num_of_columns * 2)

        row = 0
        col = 0

        # Establece los encabezados de las columnas
        header_labels = ["Module", "Status"] * num_of_columns
        self.table.setHorizontalHeaderLabels(header_labels)

        # Colores para los niveles de cumplimiento
        colors = {
            'None': QColor('red'),
            'low': QColor('orange'),
            'medium': QColor('yellow'),
            'high': QColor('green'),
        }        

        # Rellena la tabla con los datos de los módulos
        for i, (key, value) in enumerate(self.modules[0].items()):
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

            self.table.setItem(row, col*2, module_item)
            self.table.setItem(row, col*2 + 1, status_item)
            row += 1

            if row >= 12:
                row = 0
                col += 1
        
        # Conecta la señal cellClicked de la tabla a la función que abre la ventana detallada
        self.table.cellClicked.connect(self.__open_detailed_window)

        # Autoajusta las columnas y filas de la tabla
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        # Permite que la ventana de diálogo se redimensione para adaptarse a su contenido
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Añade la tabla al layout
        vbox.addWidget(self.table)

        # Crea el layout para las tres columnas y dos filas
        grid_Title = QGridLayout()
        grid_layout = QGridLayout()

        # Establece la distancia entre las columnas
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)

        # Agrega etiquetas con los nombres en la primera fila
        label1 = QLabel("LOW")
        label2 = QLabel("MEDIUM")
        label3 = QLabel("HIGH")
        texto = QLabel("Porcentaje de Cumplimiento con los\nniveles de seguridad de las Guias de Configuración Segura")
        texto.setAlignment(Qt.AlignCenter)
        texto.setStyleSheet("text-align: justify;")

        booleans_low = get_booleans(self.hostname, security_level="low")
        booleans_medium = get_booleans(self.hostname, security_level="medium")
        booleans_high = get_booleans(self.hostname, security_level="high")

        percent_low = QLabel(f"{self.__get_true_percentage(booleans_low):.2f}%")
        percent_medium = QLabel(f"{self.__get_true_percentage(booleans_medium):.2f}%")
        percent_high = QLabel(f"{self.__get_true_percentage(booleans_high):.2f}%")

        # Alinea los textos al centro
        label1.setAlignment(Qt.AlignCenter)
        label2.setAlignment(Qt.AlignCenter)
        label3.setAlignment(Qt.AlignCenter)
        percent_low.setAlignment(Qt.AlignCenter)
        percent_medium.setAlignment(Qt.AlignCenter)
        percent_high.setAlignment(Qt.AlignCenter)

        # Agrega widgets a las celdas del layout
        grid_Title.addWidget(texto, 0, 0)
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(label2, 0, 1)
        grid_layout.addWidget(label3, 0, 2)
        grid_layout.addWidget(percent_low, 1, 0)
        grid_layout.addWidget(percent_medium, 1, 1)
        grid_layout.addWidget(percent_high, 1, 2)  

        grid_Title.setAlignment(Qt.AlignCenter)
        grid_layout.setAlignment(Qt.AlignCenter)  # Alinea el layout al centro

        # Agrega el grid layout al layout principal
        vbox.addLayout(grid_Title)
        vbox.addLayout(grid_layout)

        self.setLayout(vbox)

        # Cálculo del tamaño total de la tabla y establecimiento del tamaño de la ventana
        table_width = self.table.verticalHeader().width() + 12  # for the margins
        for i in range(self.table.columnCount()):
            table_width += self.table.columnWidth(i)

        table_height = self.table.horizontalHeader().height() + 65
        for i in range(self.table.rowCount()):
            table_height += self.table.rowHeight(i)

        # Agregar un margen para el título de la ventana y los bordes
        window_margin = 30  
        self.resize(table_width + window_margin, table_height + window_margin)
        
        # Limitar la altura y anchura máxima de la ventana
        self.setMaximumHeight(800)
        self.setMaximumWidth(1200)

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
        if column % 2 == 1:  # Si se ha hecho clic en una columna de "Status"
            module_item = self.table.item(row, column - 1) # Obtiene el módulo de la columna anterior
            module_key = module_item.text() if module_item else ''
            value = self.table.item(row, column)
            if value.text():
                detailed_window = DetailedWindow(self.hostname, module_key)
                detailed_window.exec_()