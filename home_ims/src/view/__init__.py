from PyQt6 import uic

import view.util as util
from view.inventory import InventoryView
from view.history import HistoryView

def show_window(dba):
    window = uic.loadUi(util.get_ui_path("main.ui"))

    window.userSelector.addItem("<None>", False)
    for user in dba.dynamic_query("User", "Select users"):
        window.userSelector.addItem(user['name'], user['is_parent'])

    inventory_tab = InventoryView(window, dba)
    history_tab = HistoryView(window, dba)

    def on_user_change(i):
        enabled = i != 0
        inventory_tab.set_enabled(enabled)

        user = window.userSelector.itemText(i)
        privileged = window.userSelector.itemData(i)

        window.editStorageBtn.setEnabled(privileged)
        window.editLocationsBtn.setEnabled(privileged)
        window.editUsersBtn.setEnabled(privileged)

        inventory_tab.configure_user(user, privileged)

    window.userSelector.currentIndexChanged.connect(on_user_change)

    def on_tab_change(i):
        tab = window.tabs.widget(i).objectName()
        if tab == "recipesTab":
            pass
        elif tab == "mealsTab":
            pass
        elif tab == "historyTab":
            history_tab.rebuild_ui()
        elif tab == "purchasesTab":
            pass
        elif tab == "analyticsTab":
            pass
        else:
            inventory_tab.rebuild_ui()

    window.tabs.currentChanged.connect(on_tab_change)
    window.tabs.setCurrentIndex(0)
    on_tab_change(0)
    on_user_change(0)

    # TODO Connect buttons

    window.show()
