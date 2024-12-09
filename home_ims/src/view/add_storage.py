from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_storage.ui"))

def show(window, dba):
    locations = dba.select_locations()
    if not locations.is_success():
        util.open_error_dialog(window)
        return

    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        form.typeSelector.addItem("Generic Storage", dba.add_storage)
        form.typeSelector.addItem("Generic Appliance", dba.add_appliance_storage)
        form.typeSelector.addItem("Dry Storage", dba.add_dry_storage)
        form.typeSelector.addItem("Fridge", dba.add_fridge_storage)
        form.typeSelector.addItem("Freezer", dba.add_freezer_storage)

        for l in locations.get_data_list():
            form.locationSelector.addItem(l["name"])

        def create():
            name = form.nameInput.text()
            if not name.strip():
                util.open_error_dialog(window, "No name given.")
                return

            result = form.typeSelector.currentData()(name, form.locationSelector.currentText())
            if not result.is_success():
                util.open_error_dialog(window)
                return

            close_dlg()
        
        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)

        return widget

    util.open_dialog(window, gen_widget)
