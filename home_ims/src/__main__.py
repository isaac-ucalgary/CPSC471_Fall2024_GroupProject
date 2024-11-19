import sys

from PyQt6 import QtWidgets, uic

def click():
    print("Hello, world!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = uic.loadUi("mainwindow.ui")
    window.pushButton.pressed.connect(click)
    window.show()
    app.exec()

