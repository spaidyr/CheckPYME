"""
Módulo principal de la aplicación.

Este módulo es la entrada a la aplicación. Inicia la interfaz de usuario
y establece el bucle de eventos principal.
"""
from PyQt5.QtWidgets import QApplication
from App.MyApp import MyApp
import sys


def main():    
    """
    Función principal de la aplicación.

    Crea una instancia de QApplication y la interfaz de usuario.
    Luego inicia el bucle de eventos.
    """
    app = QApplication(sys.argv)

    ex = MyApp()
    ex.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
