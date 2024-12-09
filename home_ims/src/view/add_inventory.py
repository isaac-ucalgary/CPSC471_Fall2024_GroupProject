from PyQt6 import uic
from PyQt6.QtCore import Qt

from view import util
from action_result import ActionResult

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_item.ui"))

def show(window, dba, refresh):
    item_types = dba.select_item_type()
    if not item_types.is_success():
        util.open_error_dialog(window)
        return
    
    storages = dba.select_storage()
    if not storages.is_success():
        util.open_error_dialog(window)
        return

    parents = dba.select_parents()
    if not parents.is_success():
        util.open_error_dialog(window)
        return

    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        for t in item_types.get_data_list():
            form.itemSelector.addItem(t["name"], t["unit"])

        for s in storages.get_data_list():
            storage_name = s["storage_name"]
            location_name = s["location_name"]
            label = f"{storage_name} ({location_name})"
            form.storageSelector.addItem(label, storage_name)
 
        for u in parents.get_data_list():
            form.userSelector.addItem(u["name"])

        def on_item_change(i):
            unit = form.itemSelector.itemData(i)
            form.unit.setVisible(bool(unit))
            form.unit.setText(unit)

        on_item_change(0)

        form.itemSelector.currentIndexChanged.connect(on_item_change)
        util.config_dateedit(form.expiryInput)
        form.canExpire.checkStateChanged.connect(
            lambda s: form.expiryData.setVisible(s == Qt.CheckState.Checked)
        )
        form.isPurchased.checkStateChanged.connect(
            lambda s: form.purchaseData.setVisible(s == Qt.CheckState.Checked)
        )

        def create():
            quantity:float
            try:
                quantity = float(form.quantityInput.text())
                if quantity <= 0:
                    raise ValueError("Quantity not positive.")
            except ValueError:
                util.open_error_dialog(window, "Invalid quantity.")
                return

            result:ActionResult
            expiryDate = None
            if form.canExpire.checkState() == Qt.CheckState.Checked:
                expiryDate = form.expiryInput.dateTime().toPyDateTime()
 
            if form.isPurchased.checkState() == Qt.CheckState.Checked:
                try:
                    price = float(form.priceInput.text())
                    if price < 0:
                        raise ValueError("Price is negative.")
                    result = dba.purchase_item(
                        form.itemSelector.currentText(),
                        quantity,
                        form.priceInput.text(),
                        form.storeInput.text(),
                        form.userSelector.currentText(),
                        form.storageSelector.currentData(),
                        expiryDate
                    )
                except ValueError:
                    util.open_error_dialog(window, "Invalid price.")
                    return
            else:
                result = dba.add_item_to_inventory(
                    form.itemSelector.currentText(),
                    form.storageSelector.currentData(),
                    expiryDate,
                    quantity
                )

            if not result.is_success():
                print(result.get_exception())
                util.open_error_dialog(window)
                return

            close_dlg()
            refresh()

        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)
    
        return widget
    
    util.open_dialog(window, gen_widget)

