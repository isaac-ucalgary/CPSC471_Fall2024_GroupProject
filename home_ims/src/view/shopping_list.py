from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt

from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "shopping_list.ui"))

def show(window, dba):
    shopping_list = dba.gen_shopping_list()
    if not shopping_list.is_success():
        util.open_error_dialog(window)
        return

    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        text = []
        for e in shopping_list.get_data_list():
            name = e["food_name"]
            quantity = util.format_quantity(e["quantity"], e["unit"])
            text.append(f"- {quantity} {name}")

        form.listText.setText("\n".join(text))
        form.closeBtn.clicked.connect(close_dlg)
        form.copyBtn.clicked.connect(lambda: QApplication.clipboard().setText("test"))

        return widget

    util.open_dialog(window, gen_widget)
