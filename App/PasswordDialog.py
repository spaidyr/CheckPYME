from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox

KIBANA_YML = 'C:\\Elastic\\Kibana\\8.8.0\\kibana-8.8.0\\config\\kibana.yml'

class PasswordDialog(QDialog):
    """
    A custom QDialog that prompts the user to enter a password.
    """
    def __init__(self):
        """
        Initializes the PasswordDialog with a QLineEdit for password input and a submit QPushButton.
        """
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
        """
        Retrieves the text from the QLineEdit and calls the modify_yml method to update the password in the YML file.
        Finally, closes the dialog.
        """
        password = self.password_line_edit.text()

        self.modify_yml(password)
        self.close()

    def modify_yml(self, password):
        """
        Modifies the Kibana YML configuration file to replace the old password with the new one.

        Args:
            password (str): The new password to be set.
        """
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
