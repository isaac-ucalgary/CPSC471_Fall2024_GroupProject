import sys

from PyQt6 import QtWidgets, uic

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = uic.loadUi("/home/daniel/Downloads/MainWindow.ui")
    window.show()
    app.exec()

