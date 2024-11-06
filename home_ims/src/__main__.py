import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPalette, QColor



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Home IMS")

        self.buttonClicks = 0
        self.button = QPushButton("Press Me!")
        self.button.clicked.connect(self.buttonClickMethod)
        self.button.resize(200, 150)
        self.button.move(150,150)

        hbox = QHBoxLayout()
        
        hbox.addWidget(Color('white'))
        hbox.addWidget(self.button)
        hbox.addWidget(Color('white'))

        vbox = QVBoxLayout()
        
        vbox.addWidget(Color('white'))
        vbox.addLayout(hbox)
        vbox.addWidget(Color('white'))


        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)




    def buttonClickMethod(self) -> None:
        if self.buttonClicks % 2 == 0:
            self.button.setStyleSheet('QPushButton {background-color: #1FCB5E}')
        else:
            self.button.setStyleSheet('QPushButton {background-color: #CB1F95}')

        self.buttonClicks += 1


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

