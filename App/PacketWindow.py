from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from handler.Installer.packet import AgentFilePacket

class PacketWindow(QWidget):
    """
    Clase para crear una ventana de GUI de PyQt que permite al usuario iniciar 
    la compilación del paquete instalados del cliente.
    """
    def __init__(self):
        """
        Inicializa la ventana de PyQt con un QLabel y un QPushButton.
        """
        super(PacketWindow, self).__init__()

        self.setWindowTitle("Compilación")

        self.label = QLabel()
        self.label.setText("Presiona el botón para iniciar la compilación")
        
        self.compile_button = QPushButton("Iniciar compilación")
        self.compile_button.clicked.connect(self.start_compilation)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.compile_button)

        self.setLayout(layout)

    def start_compilation(self):
        """
        Inicia la compilación al ser llamado. Cambia el texto del QLabel y desactiva el QPushButton.
        También crea una instancia de la clase AgentFilePacket que lleva a cabo la compilación.
        """
        self.label.setText("La compilación está en curso...")
        self.compile_button.setEnabled(False)
        QApplication.processEvents()  # Procesar todos los eventos pendientes
        self.agent_file_packet = AgentFilePacket()  # Ejecutamos la compilación en el hilo principal
        self.label.setText("LA COMPILACIÓN HA TERMINADO")
    


