import sys

from PyQt6 import QtWidgets, uic

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = uic.loadUi("ui/main.ui")

    gen, base = uic.loadUiType("ui/inv_entry.ui")

    for i in range(30):
        widget = base()
        form = gen()
        form.setupUi(widget)
        form.quantity.setText(f"{i} mL")
        window.inventoryEntries.layout().addWidget(widget)

    window.inventoryEntries.layout().addStretch()

    window.show()
    app.exec()
