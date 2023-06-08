from PyQt5.QtWidgets import QProgressDialog

class InstallDialog(QProgressDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Installing...')
        self.setLabelText('Installing Elasticsearch and Kibana...')
        self.setCancelButton(None)
        self.setRange(0, 0)
        self.setModal(True)
        self.resize(500, 300)
