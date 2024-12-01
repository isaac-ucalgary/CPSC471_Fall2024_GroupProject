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
    window.inventoryView.setWidget(container)
    
    for entry in inv:
        form = entry_form()
        widget = entry_base()
        form.setupUi(widget)

        form.itemType.setText(entry[0])
        form.quantity.setText(f"{entry[4]:.1f} {entry[5]}")
        form.consumeBtn.clicked.connect(gen_consume_slot(dba, widget))
        form.throwOutBtn.clicked.connect(gen_throw_out_slot(dba, widget))
        form.removeBtn.clicked.connect(gen_remove_slot(dba, widget))

        if entry[3] is None:
            form.expiration.hide()
        else:
            form.expiration.setText(entry[3].strftime("Expires %-d %b, %Y"))

        c_layout.addWidget(widget)

    c_layout.addStretch()

def gen_consume_slot(dba, widget):
    remove = gen_remove_slot(dba, widget)
    def consume():
        remove()
        # TODO Log as consumed.
    return consume

def gen_throw_out_slot(dba, widget):
    remove = gen_remove_slot(dba, widget)
    def throw_out():
        remove()
        # TODO Log as wasted.
    return throw_out

def gen_remove_slot(dba, widget):
    def remove():
        # TODO Remove from inventory.
        widget.deleteLater()
    return remove

def configure_privileged(window, privileged):
    window.addItemBtn.setEnabled(privileged)
