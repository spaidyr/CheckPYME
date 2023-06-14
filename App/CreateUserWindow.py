from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox
from handler.elastic_handler import create_user

class CreateUserWindow(QWidget):
    """
    Clase que implementa una interfaz de usuario para la creación de un nuevo usuario en el servidor Elasticsearch.
    
    Attributes
    ----------
    username_label : QLabel
        Etiqueta para el campo de nombre de usuario.
    username_edit : QLineEdit
        Campo de texto para ingresar el nombre de usuario.
    password_label : QLabel
        Etiqueta para el campo de contraseña.
    password_edit : QLineEdit
        Campo de texto para ingresar la contraseña.
    create_button : QPushButton
        Botón para enviar la solicitud de creación de usuario.
    """
    def __init__(self):
        """
        Constructor de la clase. Inicializa la interfaz de usuario.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Inicializa la interfaz de usuario. Consiste en dos campos de texto para el nombre de usuario y la 
        contraseña, y un botón para enviar la solicitud de creación de usuario. Los campos de texto están 
        etiquetados con 'Username' y 'Password', respectivamente. Al hacer clic en el botón, se llama a la 
        función 'create_user_button_clicked'.
        """
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
        """
        Función que se ejecuta cuando se hace clic en el botón de creación de usuario. Recoge los valores de los 
        campos de texto para el nombre de usuario y la contraseña y los pasa a la función 'create_user' del 
        módulo 'elastic_handler', que crea el usuario en el servidor Elasticsearch. Después de la creación del usuario,
        almacena las credenciales en un archivo y muestra un cuadro de mensaje con el resultado de la operación.
        """
        username = self.username_edit.text()
        password = self.password_edit.text()
        roles = ['index_checkpyme']  # Este es el rol predefinido
        msg = create_user(username, password, roles)
        self.store_credentials(username, password)  # Almacena las credenciales en un archivo
        QMessageBox.information(self, " ", msg)
        self.close()
    
    def store_credentials(self, username, password, filename="./Agent/elk_credentials.txt"):
        """
        Almacena las credenciales del usuario en un archivo. Por defecto, el archivo es './Agent/elk_credentials.txt', 
        pero se puede especificar un nombre de archivo diferente.

        Parameters
        ----------
        username : str
            Nombre de usuario a almacenar.
        password : str
            Contraseña del usuario a almacenar.
        filename : str, optional
            Ruta y nombre del archivo en el que se almacenarán las credenciales. Por defecto, es './Agent/elk_credentials.txt'.
        """
        with open(filename, "w") as file:
            file.write(f"{username}:{password}")


