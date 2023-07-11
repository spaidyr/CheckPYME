from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QTableWidget, QTableWidgetItem, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from handler.function import get_policie as get_policie
from handler.function import get_booleans_policie as get_booleans

class DetailedWindow(QDialog):
    """
    Clase para la ventana de diálogo que muestra detalles de un módulo específico para un host.
    Esta ventana de diálogo muestra una tabla con los valores parametrizados de una poliítica concreta 
    y su estado, así como la información sobre el cumplimiento de los niveles de seguridad para cada
    una de ellas.

    Attributes
    ----------
    hostname : str
        El nombre del host para el que se muestran los detalles.
    module_key : str
        La clave de la política para la que se muestran los detalles.
    """
    def __init__(self, hostname, module_key):
        """
        Constructor de la clase. Inicializa los atributos y llama a la función para construir la interfaz de usuario.
        
        Parameters
        ----------
        hostname : str
            El nombre del host para el que se muestran los detalles.
        module_key : str
            La clave de la política para la que se muestran los detalles.
        """
        super().__init__()
        self.hostname = hostname
        self.module_key = module_key
        self.__initUI()

    def __initUI(self):
        """
        Inicializa la interfaz de usuario para la ventana de diálogo. Esta interfaz consiste en una tabla
        que muestra las políticas del módulo y su estado para el host y el módulo seleccionados y una serie 
        de etiquetas y widgets que muestran información adicional sobre los niveles de seguridad.

        La tabla se llena con los datos de las políticas obtenidos del archivo de configuración. Cada fila
        de la tabla representa una política y tiene dos columnas: el nombre de la política y su estado. El estado
        de la política se colorea de acuerdo a su nivel de cumplimiento, usando rojo para 'Ninguno', naranja
        para 'bajo', amarillo para 'medio' y verde para 'alto'.

        Por debajo de la tabla, se muestra información adicional sobre el cumplimiento de los niveles de
        seguridad en forma de porcentajes. Esto se presenta en tres columnas para los niveles 'bajo',
        'medio' y 'alto', respectivamente. Los porcentajes se calculan utilizando la función
        'get_true_percentage' y representan la proporción de políticas con valor 'True' para cada nivel
        de seguridad.
        """
        self.setWindowTitle(f'{self.module_key} on {self.hostname}')
        #self.setGeometry(1100, 100, 307, 400)

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

        # Autoajusta las columnas y filas de la tabla
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        # Permite que la ventana de diálogo se redimensione para adaptarse a su contenido
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        vbox.addWidget(table)

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

        booleans_low = get_booleans(self.hostname, self.module_key, security_level="low")
        booleans_medium = get_booleans(self.hostname, self.module_key, security_level="medium")
        booleans_high = get_booleans(self.hostname, self.module_key, security_level="high")

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
        table_width = table.verticalHeader().width() + 12  # for the margins
        for i in range(table.columnCount()):
            table_width += table.columnWidth(i)

        table_height = table.horizontalHeader().height() + 65
        for i in range(table.rowCount()):
            table_height += table.rowHeight(i)

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