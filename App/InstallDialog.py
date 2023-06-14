from PyQt5.QtWidgets import QProgressDialog

class InstallDialog(QProgressDialog):
    """
    Clase para crear una ventana de diálogo de instalación en PyQt. Esta ventana de diálogo
    muestra una barra de progreso indefinida mientras se instalan Elasticsearch y Kibana. 
    Este diálogo no puede ser cancelado por el usuario y bloqueará el acceso a otros widgets mientras esté abierto.
    """
    def __init__(self, parent=None):
        """
        Inicializa la ventana de diálogo de instalación con un título, una etiqueta,
        desactiva el botón de cancelar, establece un rango indefinido para la barra de progreso, 
        habilita el modal y establece un tamaño específico para la ventana.

        Parámetros:
        parent : QWidget, optional
            El widget padre de esta ventana de diálogo. Por defecto es None.
        """
        super().__init__(parent)
        self.setWindowTitle('Installing...')
        self.setLabelText('Installing Elasticsearch and Kibana...')
        self.setCancelButton(None)
        self.setRange(0, 0)
        self.setModal(True)
        self.resize(500, 300)
