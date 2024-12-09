from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QDateTime
from PyQt6 import uic

import view.add_inventory as add_inventory
from view import util
from Database import Database
DB_Actions = Database.DB_Actions

entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("inv_entry.ui"))
info_form_tpl, info_base_tpl = uic.loadUiType(util.get_ui_path("popup", "item_info.ui"))
consume_form_tpl, consume_base_tpl = uic.loadUiType(util.get_ui_path("popup", "consume_item.ui"))
waste_form_tpl, waste_base_tpl = uic.loadUiType(util.get_ui_path("popup", "waste_item.ui"))
remove_form_tpl, remove_base_tpl = uic.loadUiType(util.get_ui_path("popup", "delete_item.ui"))

class InventoryView:
    def __init__(self, window, dba:DB_Actions):
        self.window = window
        self.dba:DB_Actions = dba

        self.window.addItemBtn.clicked.connect(
            lambda: add_inventory.show(self.window, self.dba, self.update_view)
        )
        self.window.refreshInventoryBtn.clicked.connect(self.update_view)
        self.window.filterExpiry.checkStateChanged.connect(
            lambda s: self.window.expiryInput.setVisible(s == Qt.CheckState.Checked)
        )

        self.window.filterExpiry.setCheckState(Qt.CheckState.Unchecked)
        self.window.expiryInput.setVisible(False)

    def rebuild_ui(self):
        self.window.inventorySearch.clear()
        self.window.storageSelector.clear()
        self.window.filterExpiry.setCheckState(Qt.CheckState.Unchecked)
        self.window.expiryInput.setDateTime(QDateTime.currentDateTime())

        storages = self.dba.select_storage()
        if not storages.is_success():
            util.open_error_dialog(self.window)
            return

        self.window.storageSelector.addItem("<Any storage>", "")
        for s in storages.get_data_list():
            storage_name = s["storage_name"]
            location_name = s["location_name"]
            self.window.storageSelector.addItem(f"{storage_name} ({location_name})", s["storage_name"])

        self.update_view()

    def update_view(self):
        expiry_threshold = None
        if self.window.filterExpiry.checkState() == Qt.CheckState.Checked:
            expiry_threshold = self.window.expiryInput.dateTime().toPyDateTime()

        inv = self.dba.view_inventory_items(
            self.window.inventorySearch.text(),
            self.window.storageSelector.currentData(),
            expiry_threshold
        )

        if not inv.is_success():
            util.open_error_dialog(self.window)
            return

        c_layout = QVBoxLayout()
        container = QWidget()
        container.setProperty("nobackground", True)
        container.setLayout(c_layout)

        for entry in inv.get_data_list():
            widget = entry_base_tpl()
            form = entry_form_tpl()
            form.setupUi(widget)

            form.itemType.setText(entry["item_name"])
            form.quantity.setText(util.format_quantity(entry["quantity"], entry["unit"]))
            form.infoBtn.clicked.connect(lambda _, e=entry: self.item_info(e))
            form.consumeBtn.clicked.connect(lambda _, e=entry: self.consume_item(e))
            form.throwOutBtn.clicked.connect(lambda _, e=entry: self.throw_out_item(e))
            form.removeBtn.clicked.connect(lambda _, e=entry: self.remove_item(e))

            if entry["expiry"] is None:
                form.expiry.hide()
            else:
                form.expiry.setText("Expires " + util.format_date(entry["expiry"]))

            c_layout.addWidget(widget)

        c_layout.addStretch()

        self.window.inventoryView.setWidget(container)

    def configure_user(self, user, privileged):
        self.window.addItemBtn.setEnabled(privileged)
        for widget in self.window.inventoryView.widget().findChildren(QWidget, "removeBtn"):
            widget.setEnabled(privileged)

    def item_info(self, entry):
        def gen_dialog(close_dlg):
            widget = info_base_tpl()
            form = info_form_tpl()
            form.setupUi(widget)
            
            if entry["expiry"] is not None:
                form.expirationLabel.setText(util.format_date(entry["expiry"]))
            else:
                form.expiration.hide()

            form.item.setText(entry["item_name"])
            form.quantity.setText(util.format_quantity(entry["quantity"], entry["unit"]))
            form.storage.setText(entry["storage_name"])
            form.location.setText(entry["location_name"])
            form.closeBtn.clicked.connect(close_dlg)

            return widget

        util.open_dialog(self.window, gen_dialog)            

    def consume_item(self, entry):
        users = self.dba.select_users()
        if not users.is_success():
            util.open_error_dialog(self.window)
            return

        def gen_dialog(close_dlg):
            widget = consume_base_tpl()
            form = consume_form_tpl()
            form.setupUi(widget)

            for u in users.get_data_list():
                form.userSelector.addItem(u["name"])

            def consume():
                quantity:float
                try:
                    quantity = float(form.quantityInput.text())
                    if quantity <= 0 or quantity > entry["quantity"]:
                        raise ValueError("Quantity not positive.")
                except ValueError:
                    util.open_error_dialog(self.window, "Invalid quantity.")
                    return

                result = self.dba.consume_inventory(
                    entry["item_name"],
                    entry["storage_name"],
                    entry["timestamp"],
                    quantity,
                    form.userSelector.currentText()
                )
                if not result.is_success():
                    util.open_error_dialog(self.window)
                    return

                self.update_view() # TODO Update only this entry.
                close_dlg()

            form.item.setText(entry["item_name"])
            form.currentQuantity.setText(util.format_quantity(entry["quantity"], entry["unit"]))
            form.cancelBtn.clicked.connect(close_dlg)
            form.consumeBtn.clicked.connect(consume)

            return widget
        
        util.open_dialog(self.window, gen_dialog)

    def throw_out_item(self, entry):
        def gen_dialog(close_dlg):
            widget = waste_base_tpl()
            form = waste_form_tpl()
            form.setupUi(widget)

            def waste():
                quantity:float
                try:
                    quantity = float(form.quantityInput.text())
                    if quantity <= 0 or quantity > entry["quantity"]:
                        raise ValueError("Quantity not positive.")
                except ValueError:
                    util.open_error_dialog(self.window, "Invalid quantity.")
                    return

                result = self.dba.throw_out_inventory(
                    entry["item_name"],
                    entry["storage_name"],
                    entry["timestamp"],
                    quantity
                )
                if not result.is_success():
                    util.open_error_dialog(self.window)
                    return

                self.update_view() # TODO Update only this entry.
                close_dlg()

            form.item.setText(entry["item_name"])
            form.currentQuantity.setText(util.format_quantity(entry["quantity"], entry["unit"]))
            form.cancelBtn.clicked.connect(close_dlg)
            form.wasteBtn.clicked.connect(waste)

            return widget
        
        util.open_dialog(self.window, gen_dialog)

    def remove_item(self, entry):
        def gen_dialog(close_dlg):
            widget = remove_base_tpl()
            form = remove_form_tpl()
            form.setupUi(widget)

            def delete():
                result = self.dba.dynamic_query(
                    "Inventory",
                    "Remove item from inventory",
                    item_name=entry["item_name"],
                    storage_name=entry["storage_name"],
                    timestamp=entry["timestamp"]
                )
                if not result.is_success():
                    util.open_error_dialog(self.window)
                    return

                self.update_view() # TODO Update only this entry.
                close_dlg()

            form.item.setText(entry["item_name"])
            form.cancelBtn.clicked.connect(close_dlg)
            form.deleteBtn.clicked.connect(delete)

            return widget
        
        util.open_dialog(self.window, gen_dialog)
