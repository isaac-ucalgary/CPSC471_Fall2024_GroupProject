from re import purge
from PyQt6 import uic
from mysql.connector.types import RowType

import view.util as util
from view.inventory import InventoryView
from view.history import HistoryView
from view.purchases import PurchasesView
from view.analytics import AnalyticsView
from Return_Formatted import Return_Formatted
from Database import Database
DB_Actions = Database.DB_Actions

def show_window(dba:DB_Actions):
    window = uic.loadUi(util.get_ui_path("main.ui"))

    # Insure that window was created
    if window is None:
        return

    window.userSelector.addItem("<None>", False)

    for user in dba.select_users().get_data_list():
        window.userSelector.addItem(user['name'], user['is_parent'])

    inventory_tab = InventoryView(window, dba)
    history_tab = HistoryView(window, dba)
    purchases_tab = PurchasesView(window, dba)
    analytics_tab = AnalyticsView(window, dba)

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
        match tab:
            case "recipesTab":
                pass
            case "mealsTab":
                pass
            case "historyTab":
                history_tab.rebuild_ui()
            case "purchasesTab":
                purchases_tab.rebuild_ui()
            case "analyticsTab":
                analytics_tab.rebuild_ui()
            case _:
                inventory_tab.rebuild_ui()

    window.tabs.currentChanged.connect(on_tab_change)
    window.tabs.setCurrentIndex(0)
    on_tab_change(0)
    on_user_change(0)

    # TODO Connect buttons

    window.show()
