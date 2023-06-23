import json
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QGroupBox, QCheckBox

class ConfigWindow(QDialog):
    """
    Clase que implementa una ventana de diálogo para la configuración de la aplicación.

    Attributes
    ----------
    parent : QWidget
        El widget padre de la ventana de configuración. 
    saveButton : QPushButton
        Botón para guardar los cambios en la configuración.
    layout : QVBoxLayout
        Layout principal para la ventana de diálogo.
    config_widgets : dict
        Diccionario para almacenar las referencias a los widgets que contienen los valores de configuración.
    old_config : dict
        Diccionario para almacenar la configuración original leída del archivo de configuración.
    """
    def __init__(self, parent=None):
        """
        Constructor de la clase. Inicializa la interfaz de usuario y carga la configuración existente desde el archivo de configuración.
        """
        super(ConfigWindow, self).__init__(parent)
        self.parent = parent

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.__save_config)

        self.layout = QVBoxLayout()

        self.config_widgets = {}
        self.__load_config()

        self.layout.addWidget(self.saveButton)

        self.setLayout(self.layout)

    def __load_config(self):
        """
        Carga la configuración desde el archivo 'config.json'. Para cada sección de la configuración, se crea un QGroupBox. 
        Dentro de cada QGroupBox, se crea un grid layout y se agregan widgets para cada clave y valor en la sección.
        """
        with open("config.json", "r") as file:
            self.old_config = json.load(file)

            for section in self.old_config:
                group_box = QGroupBox(section)
                grid_layout = QGridLayout()
                row = 0

                for i, config in enumerate(self.old_config[section]):
                    for config_key, config_value in config.items():
                        grid_layout.addWidget(QLabel(config_key), row, 0)

                        if section == "modules":
                            checkBox = QCheckBox()
                            checkBox.setChecked(config_value.lower() == "true")
                            checkBox.setObjectName(f"{section}_{i}_{config_key}")
                            grid_layout.addWidget(checkBox, row, 1)
                            
                            self.config_widgets[f"{section}_{i}_{config_key}"] = checkBox
                        else:
                            lineEdit = QLineEdit(str(config_value))
                            lineEdit.setObjectName(f"{section}_{i}_{config_key}")
                            grid_layout.addWidget(lineEdit, row, 1)
                            
                            self.config_widgets[f"{section}_{i}_{config_key}"] = lineEdit
                            
                        row += 1

                group_box.setLayout(grid_layout)
                self.layout.addWidget(group_box)

    def __save_config(self):
        """
        Guarda la configuración en el archivo 'config.json'. Recoge los valores de los widgets y los guarda en el diccionario 
        de configuración. Luego vuelca el diccionario en el archivo de configuración. Después de guardar la configuración, 
        llama a la función 'update_agent_json' para actualizar el archivo 'agent.json'. Si se han modificado los ajustes del 
        servidor, muestra un cuadro de mensaje informando al usuario de que debe reiniciar la aplicación.
        """
        restart_needed = False
        for section in self.old_config:
            for i, config in enumerate(self.old_config[section]):
                for config_key in config:
                    # Update the configuration value using the widget reference from the config_widgets dictionary
                    if section == "modules":
                        self.old_config[section][i][config_key] = str(self.config_widgets[f"{section}_{i}_{config_key}"].isChecked()).lower()
                    else:
                        new_value = self.config_widgets[f"{section}_{i}_{config_key}"].text()
                        if section == "configuration" and self.old_config[section][i][config_key] != new_value:
                            restart_needed = True
                        self.old_config[section][i][config_key] = new_value

        with open("config.json", "w") as file:
            json.dump(self.old_config, file, indent=4)
        
        self.update_agent_json()

        if restart_needed:
            QMessageBox.information(self, "Changes Saved", "The configuration changes have been saved. Since you modified the server settings, please restart the application.")
            self.parent.quit()
        self.close()  # Close the window after saving changes

    def update_agent_json(self):
        """
        Actualiza el archivo 'agent.json' con el nuevo valor del 'server_ip' obtenido de 'config.json'. 
        El archivo 'agent.json' se abre en modo de lectura y escritura, se carga el contenido en un diccionario, 
        se actualiza el valor de 'server_ip', se escribe el nuevo contenido en el archivo y luego se trunca el archivo 
        en caso de que el nuevo contenido sea más pequeño que el original.
        """
        # Abre el archivo "agent.json" para su actualización
        with open("./Agent/config.json", "r+") as file:
            # Carga el contenido del archivo
            data = json.load(file)

            # Actualiza el valor de "server_ip" con el valor obtenido de "config.json"
            data['server_ip'] = self.old_config["configuration"][0]["server_ip"]

            # Posiciona el puntero al inicio del archivo
            file.seek(0)

            # Escribe el nuevo contenido al archivo
            json.dump(data, file, indent=4)

            # Trunca el archivo en caso de que el nuevo contenido sea más pequeño que el original
            file.truncate()