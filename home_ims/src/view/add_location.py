from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from action_result import ActionResult
from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_location.ui"))

def show(window, dba):
    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        def create():
            name = form.nameInput.text()
            if not name.strip():
                util.open_error_dialog(window, "No name given.")
                return

            result = dba.add_location(name)
            if not result.is_success():
                util.open_error_dialog(window)
                return

            close_dlg()
        
        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)

        return widget

    util.open_dialog(window, gen_widget)
