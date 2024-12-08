from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_item_type.ui"))

def show(window, dba):
    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        form.typeSelector.addItem("Durable Goods", dba.add_durable_type)
        form.typeSelector.addItem("Food Items", dba.add_food_type)
        form.typeSelector.addItem("Other Consumables", dba.add_notfood_type)

        def create():
            name = form.nameInput.text()
            if not name.strip():
                util.open_error_dialog(window, "No name given.")
                return

            result = form.typeSelector.currentData()(name, form.unitInput.text())
            if not result.is_success():
                util.open_error_dialog(window)
                return

            close_dlg()

        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)

        return widget

    util.open_dialog(window, gen_widget)
