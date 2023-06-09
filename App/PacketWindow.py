from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from handler.Installer.packet import AgentFilePacket

class PacketWindow(QWidget):
    def __init__(self):
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
        self.label.setText("La compilación está en curso...")
        self.compile_button.setEnabled(False)
        QApplication.processEvents()  # Procesar todos los eventos pendientes
        self.agent_file_packet = AgentFilePacket()  # Ejecutamos la compilación en el hilo principal
        self.label.setText("LA COMPILACIÓN HA TERMINADO")
    


