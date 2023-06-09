from PyQt5.QtWidgets import QMessageBox

class CertificatesAlert(QMessageBox):
    def __init__(self, parent=None):
        super(CertificatesAlert, self).__init__(parent)
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Certificados no encontrados")
        self.setText("No se encontraron los certificados necesarios.")
        self.setInformativeText("Puede continuar, pero el handler no se iniciará hasta que existan los certificados.")
        self.setStandardButtons(QMessageBox.Ok)
        self.buttonClicked.connect(self.closeAlert)

    def closeAlert(self):
        self.close()
