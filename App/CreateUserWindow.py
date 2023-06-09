from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox
from handler.elastic_handler import create_user

class CreateUserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.username_label = QLabel('Username', self)
        self.username_edit = QLineEdit(self)

        self.password_label = QLabel('Password', self)
        self.password_edit = QLineEdit(self)

        self.create_button = QPushButton('Create User', self)
        self.create_button.clicked.connect(self.create_user_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.create_button)

        self.setLayout(layout)
        self.show()

    def create_user_button_clicked(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        roles = ['index_checkpyme']  # Este es el rol predefinido
        msg = create_user(username, password, roles)
        self.store_credentials(username, password)  # Almacena las credenciales en un archivo
        QMessageBox.information(self, " ", msg)
        self.close()
    
    def store_credentials(self, username, password, filename="./Agent/elk_credentials.txt"):
        with open(filename, "w") as file:
            file.write(f"{username}:{password}\n")


