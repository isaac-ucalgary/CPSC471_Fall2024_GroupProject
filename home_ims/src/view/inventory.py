from PyQt6 import QtWidgets, uic

import view.util as util

entry_form, entry_base = uic.loadUiType(util.get_ui_path("inv_entry.ui"))

def setup_view(window, dba):
    inv = dba.dynamic_query(
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
        form.consumeBtn.clicked.connect(gen_consume_slot(dba, widget, entry))
        form.throwOutBtn.clicked.connect(gen_throw_out_slot(dba, widget, entry))
        form.removeBtn.clicked.connect(gen_remove_slot(dba, widget, entry))

        if entry["expiration"] is None:
            form.expiration.hide()
        else:
            form.expiration.setText(entry["expiration"].strftime("Expires %-d %b, %Y"))

        c_layout.addWidget(widget)

    c_layout.addStretch()

    window.inventoryView.setWidget(container)

def gen_consume_slot(dba, widget, entry):
    def consume():
        widget.deleteLater()
        # TODO Remove and log as consumed.
    return consume

def gen_throw_out_slot(dba, widget, entry):
    def throw_out():
        dba.dynamic_query(
            "Inventory",
            "Remove item from inventory",
            item_name=entry["item_name"],
            storage_name=entry["storage_name"],
            timestamp=entry["timestamp"]
        )
        dba.dynamic_query(
            "Wasted",
            "Add item wasted record",
            item_name=entry["item_name"],
            quantity=entry["quantity"]
        )
        widget.deleteLater()
    return throw_out

def gen_remove_slot(dba, widget, entry):
    def remove():
        widget.deleteLater()
        dba.dynamic_query(
            "Inventory",
            "Remove item from inventory",
            item_name=entry["item_name"],
            storage_name=entry["storage_name"],
            timestamp=entry["timestamp"]
        )
    return remove

def configure_privileged(window, privileged):
    window.addItemBtn.setEnabled(privileged)
    for widget in window.inventoryView.widget().children():
        if widget.objectName() == "InventoryEntry":
            widget.findChild(QtWidgets.QWidget, "removeBtn").setEnabled(privileged)
