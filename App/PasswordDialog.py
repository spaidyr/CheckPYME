from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox

KIBANA_YML = 'C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\\kibana.yml'

class PasswordDialog(QDialog):

    def __init__(self):
        super().__init__()

        #self.setGeometry(100, 100, 300, 300)  # Set window size to 300x300 pixels

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setEchoMode(QLineEdit.Password)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Por favor, introduzca la contraseña para el usuario kibana_system:"))
        layout.addWidget(self.password_line_edit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit(self):
        password = self.password_line_edit.text()

        self.modify_yml(password)
        self.close()

    def modify_yml(self, password):
        # Read the YML file
        with open(KIBANA_YML, 'r') as file:
            lines = file.readlines()

        # Replace the password
        with open(KIBANA_YML, 'w') as file:
            for line in lines:
                if "elasticsearch.password:" in line:
                    file.write(f"elasticsearch.password: \"{password}\"\n")
                else:
                    file.write(line)

        QMessageBox.information(self, 'Exito', 'La contraseña ha sido cambiada exitosamente.')
