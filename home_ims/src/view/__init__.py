from PyQt6 import uic

import view.util as util
import view.inventory

def show_window(dba):
    window = uic.loadUi(util.get_ui_path("main.ui"))

    for user in dba.dynamic_query("User", "Select users"):
        window.userSelector.addItem(user[0], user[1])
    
    def on_user_change(i):
        privileged = window.userSelector.itemData(i)

        window.editStorageBtn.setEnabled(privileged)
        window.editLocationsBtn.setEnabled(privileged)
        window.editUsersBtn.setEnabled(privileged)

        inventory.configure_privileged(window, privileged)

    window.userSelector.currentIndexChanged.connect(on_user_change)

    def on_tab_change(i):
        tab = window.tabs.widget(i).objectName()
        if tab == "recipesTab":
            pass
        elif tab == "mealsTab":
            pass
        elif tab == "historyTab":
            pass
        elif tab == "purchasesTab":
            pass
        elif tab == "analyticsTab":
            pass
        else:
            inventory.setup_view(window, dba)

    window.tabs.currentChanged.connect(on_tab_change)
    window.tabs.setCurrentIndex(0)
    on_tab_change(0)

    # TODO Connect buttons

    window.show()
