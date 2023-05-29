import json
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QGroupBox, QCheckBox

class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent)
        self.parent = parent

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save_config)

        self.layout = QVBoxLayout()

        self.config_widgets = {}
        self.load_config()

        self.layout.addWidget(self.saveButton)

        self.setLayout(self.layout)

    def load_config(self):
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

    def save_config(self):
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

        if restart_needed:
            QMessageBox.information(self, "Changes Saved", "The configuration changes have been saved. Since you modified the server settings, please restart the application.")
            self.parent.quit()
        self.close()  # Close the window after saving changes
