import handler.socket_handler as socket_handler
from PyQt5.QtWidgets import QApplication
from App.MyApp import MyApp
import sys

def run_app():
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

def main():    

    app = QApplication(sys.argv)

    ex = MyApp()
    ex.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
