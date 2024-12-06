from PyQt6 import uic

from view import util
from view.inventory import InventoryView
from view.recipes import RecipesView
from view.history import HistoryView
from view.purchases import PurchasesView
from view.analytics import AnalyticsView

def show_window(dba):
    window = uic.loadUi(util.get_ui_path("main.ui"))

    window.userSelector.addItem("<None>", False)
    for user in dba.select_users():
        window.userSelector.addItem(user['name'], user['is_parent'])

    inventory_tab = InventoryView(window, dba)
    recipes_tab = RecipesView(window, dba)
    history_tab = HistoryView(window, dba)
    purchases_tab = PurchasesView(window, dba)
    analytics_tab = AnalyticsView(window, dba)

    def on_user_change(i):
        enabled = i != 0
        window.tabs.setEnabled(enabled)
        window.shoppingListBtn.setEnabled(enabled)

        user = window.userSelector.itemText(i)
        privileged = window.userSelector.itemData(i)

        window.addStorageBtn.setEnabled(privileged)
        window.addLocationBtn.setEnabled(privileged)
        window.addUserBtn.setEnabled(privileged)

        inventory_tab.configure_user(user, privileged)
        recipes_tab.configure_user(user, privileged)

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
            purchases_tab.rebuild_ui()
        elif tab == "analyticsTab":
            analytics_tab.rebuild_ui()
        else:
            inventory_tab.rebuild_ui()

    window.tabs.currentChanged.connect(on_tab_change)
    window.tabs.setCurrentIndex(0)
    on_tab_change(0)
    on_user_change(0)

    # TODO Connect buttons

    window.show()
