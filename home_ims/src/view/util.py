import os
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import QDialog, QVBoxLayout

root = os.path.dirname(__file__)

def get_ui_path(*path):
    return os.path.join(root, "ui", *path)

def format_quantity(quantity, unit):
    return f"{quantity:.1f} {unit}"

def format_date(timestamp):
    return timestamp.strftime("%-d %b %Y")

def format_datetime(timestamp):
    return timestamp.strftime("%I:%M:%S %p, %-d %b %Y")

def open_dialog(window, cb):
    dialog = QDialog(window)
    layout = QVBoxLayout()
    layout.addWidget(cb(dialog.accept))
    dialog.setLayout(layout)
    dialog.open()

class Sorting(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def lessThan(self, left, right):
        lval = self.sourceModel().data(left, Qt.ItemDataRole.UserRole)
        rval = self.sourceModel().data(right, Qt.ItemDataRole.UserRole)

        if lval is None:
            return True
        elif rval is None:
            return False
        else:
            return lval < rval
