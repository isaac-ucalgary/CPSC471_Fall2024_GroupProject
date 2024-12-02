from PyQt6 import QtWidgets, uic

import view.util as util

entry_form, entry_base = uic.loadUiType(util.get_ui_path("inv_entry.ui"))

class InventoryView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba
        self.current_user = None
        self.rebuild_ui()
    
    def rebuild_ui(self):
        inv = self.dba.dynamic_query(
            "Inventory",
            "View items",
            item_name = "%",
            storage_name = "%",
            timestamp_from = "1000-01-01",
            timestamp_to = "9999-12-31"
        )

        container = QtWidgets.QWidget()
        c_layout = QtWidgets.QVBoxLayout()
        container.setObjectName("inventoryEntries")
        container.setStyleSheet("#inventoryEntries{background-color:#00ffffff;}")
        container.setLayout(c_layout)

        for entry in inv:
            form = entry_form()
            widget = entry_base()
            form.setupUi(widget)

            form.itemType.setText(entry["item_name"])
            form.quantity.setText(f"{entry['quantity']:.1f} {entry['unit']}")
            form.consumeBtn.clicked.connect(self.gen_consume_slot(widget, entry))
            form.throwOutBtn.clicked.connect(self.gen_throw_out_slot(widget, entry))
            form.removeBtn.clicked.connect(self.gen_remove_slot(widget, entry))

            if entry["expiration"] is None:
                form.expiration.hide()
            else:
                form.expiration.setText(entry["expiration"].strftime("Expires %-d %b, %Y"))

            c_layout.addWidget(widget)

        c_layout.addStretch()

        self.window.inventoryView.setWidget(container)

    def configure_user(self, user, privileged):
        self.current_user = user

        self.window.addItemBtn.setEnabled(privileged)
        for widget in self.window.inventoryView.widget().children():
            if widget.objectName() == "InventoryEntry":
                widget.findChild(QtWidgets.QWidget, "removeBtn").setEnabled(privileged)

    # TODO Update once dialog window is completed.
    def gen_consume_slot(self, widget, entry):
        def consume():
            self.dba.consume_inventory(
                entry["item_name"],
                entry["storage_name"],
                entry["timestamp"],
                10,
                self.current_user
            )
            self.rebuild_ui()
        return consume

    def gen_throw_out_slot(self, widget, entry):
        def throw_out():
            self.dba.throw_out_inventory(
                entry["item_name"],
                entry["storage_name"],
                entry["timestamp"],
                10
            )
            self.rebuild_ui()
        return throw_out

    def gen_remove_slot(dba, widget, entry):
        def remove():
            widget.deleteLater()
            self.dba.dynamic_query(
                "Inventory",
                "Remove item from inventory",
                item_name=entry["item_name"],
                storage_name=entry["storage_name"],
                timestamp=entry["timestamp"]
            )
        return remove
