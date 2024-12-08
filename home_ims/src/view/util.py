import os
from PyQt6 import uic
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import QDialog, QVBoxLayout

root = os.path.dirname(__file__)
def get_ui_path(*path):
    return os.path.join(root, "ui", *path)

def format_quantity(quantity, unit):
    qf = f"{quantity:.1f}".removesuffix(".0")
    return f"{qf} {unit}" if unit else qf

def format_date(timestamp):
    return timestamp.strftime("")

def format_datetime(timestamp):
    return timestamp.strftime("%I:%M:%S %p, %-d %b %Y")

def open_dialog(window, gen):
    dialog = QDialog(window)
    layout = QVBoxLayout()
    layout.addWidget(gen(dialog.accept))
    dialog.setLayout(layout)
    dialog.open()

error_form_tpl, error_widget_tpl = uic.loadUiType(get_ui_path("popup", "error_generic.ui"))
def open_error_dialog(window, msg=None):
    def gen_widget(close):
        widget = error_widget_tpl()
        form = error_form_tpl()
        form.setupUi(widget)

        if msg is not None:
            form.warningLabel.setText(msg)

        form.closeBtn.clicked.connect(close)

        return widget
    open_dialog(window, gen_widget)

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
