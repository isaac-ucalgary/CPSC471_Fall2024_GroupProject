from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QDateTime
from PyQt6 import uic

import view.add_inventory as add_inventory
from view import util
from Database import Database
DB_Actions = Database.DB_Actions

entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("inv_entry.ui"))

class InventoryView:
    def __init__(self, window, dba:DB_Actions):
        self.window = window
        self.dba:DB_Actions = dba
        self.current_user = None

        self.window.addItemBtn.clicked.connect(lambda: add_inventory.show(self.window, self.dba))
        self.window.refreshBtn.clicked.connect(self.update_inv_view)
        self.window.filterExpiry.checkStateChanged.connect(
            lambda s: self.window.expiryInput.setVisible(s == Qt.CheckState.Checked)
        )

        self.window.filterExpiry.setCheckState(Qt.CheckState.Unchecked)
        self.window.expiryInput.setDateTime(QDateTime.currentDateTime())
        self.window.expiryInput.setVisible(False)

    def rebuild_ui(self):
        self.window.storageSelector.clear()

        storages = self.dba.select_storage()
        if not storages.is_success():
            util.open_error_dialog(self.window)
            return

        self.window.storageSelector.addItem("<Any storage>", "")
        for s in storages.get_data_list():
            self.window.storageSelector.addItem(s["storage_name"], s["storage_name"])

        self.update_inv_view()

    def update_inv_view(self):
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
        container.setObjectName("inventoryEntries")
        container.setStyleSheet("#inventoryEntries{background-color:#00ffffff;}")
        container.setLayout(c_layout)

        for entry in inv.get_data_list():
            widget = entry_base_tpl()
            form = entry_form_tpl()
            form.setupUi(widget)

            form.itemType.setText(entry["item_name"])
            form.quantity.setText(util.format_quantity(entry["quantity"], entry["unit"]))
            form.consumeBtn.clicked.connect(self.gen_consume_slot(entry))
            form.throwOutBtn.clicked.connect(self.gen_throw_out_slot(entry))
            form.removeBtn.clicked.connect(self.gen_remove_slot(entry))

            if entry["expiry"] is None:
                form.expiry.hide()
            else:
                form.expiry.setText("Expires " + util.format_date(entry["expiry"]))

            c_layout.addWidget(widget)

        c_layout.addStretch()

        self.window.inventoryView.setWidget(container)

    def configure_user(self, user, privileged):
        self.current_user = user

        self.window.addItemBtn.setEnabled(privileged)
        for widget in self.window.inventoryView.widget().findChildren(QWidget, "removeBtn"):
            widget.setEnabled(privileged)

    # TODO Update once dialog window is completed.
    def gen_consume_slot(self, entry):
        def consume():
            self.dba.consume_inventory(
                entry["item_name"],
                entry["storage_name"],
                entry["timestamp"],
                10,
                self.current_user
            )
            self.update_inv_view() # TODO Update only this entry.
        return consume

    def gen_throw_out_slot(self, entry):
        def throw_out():
            self.dba.throw_out_inventory(
                entry["item_name"],
                entry["storage_name"],
                entry["timestamp"],
                10
            )
            self.update_inv_view() # TODO Update only this entry.
        return throw_out

    def gen_remove_slot(self, entry):
        def remove():
            self.dba.dynamic_query(
                "Inventory",
                "Remove item from inventory",
                item_name=entry["item_name"],
                storage_name=entry["storage_name"],
                timestamp=entry["timestamp"]
            )
            self.update_inv_view() # TODO Update only this entry.
        return remove
