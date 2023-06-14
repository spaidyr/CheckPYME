from PyQt5.QtWidgets import QMessageBox

class CertificatesAlert(QMessageBox):
    """
    Clase que representa una alerta de certificados faltantes.

    Esta clase hereda de QMessageBox y muestra un cuadro de diálogo de advertencia
    cuando no se encuentran los certificados necesarios.
    """
    def __init__(self, parent=None):
        """
        Constructor de la clase CertificatesAlert.

        Args:
            parent (QWidget): Widget padre del cuadro de diálogo (predeterminado: None).
        """
        super(CertificatesAlert, self).__init__(parent)
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Certificados no encontrados")
        self.setText("No se encontraron los certificados necesarios.")
        self.setInformativeText("Puede continuar, pero el handler no se iniciará hasta que existan los certificados.")
        self.setStandardButtons(QMessageBox.Ok)
        self.buttonClicked.connect(self.closeAlert)

    def closeAlert(self):
        """
        Método que se ejecuta cuando se hace clic en el botón de aceptar.

        Cierra el cuadro de diálogo.
        """
        self.close()
