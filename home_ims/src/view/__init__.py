from re import purge
from PyQt6 import uic
from mysql.connector.types import RowType

from view import util
from view.inventory import InventoryView
from view.recipes import RecipesView
from view.meals import MealsView
from view.history import HistoryView
from view.purchases import PurchasesView
from view.analytics import AnalyticsView

import view.shopping_list as shopping_list
import view.add_item_type as add_item_type
import view.add_storage as add_storage
import view.add_location as add_location
import view.add_user as add_user

from action_result import ActionResult
from Database import Database
DB_Actions = Database.DB_Actions

def show_window(dba:DB_Actions):
    window = uic.loadUi(util.get_ui_path("main.ui"))

    window.userSelector.addItem("<None>", False)

    for user in dba.select_users().get_data_list():
        window.userSelector.addItem(user['name'], user['is_parent'])

    inventory_tab = InventoryView(window, dba)
    recipes_tab = RecipesView(window, dba)
    meals_tab = MealsView(window, dba)
    history_tab = HistoryView(window, dba)
    purchases_tab = PurchasesView(window, dba)
    analytics_tab = AnalyticsView(window, dba)

    def on_user_change(i):
        enabled = i != 0
        window.tabs.setEnabled(enabled)
        window.shoppingListBtn.setEnabled(enabled)

        user = window.userSelector.itemText(i)
        privileged = window.userSelector.itemData(i)

        window.addItemTypeBtn.setEnabled(privileged)
        window.addStorageBtn.setEnabled(privileged)
        window.addLocationBtn.setEnabled(privileged)
        window.addUserBtn.setEnabled(privileged)

        inventory_tab.configure_user(user, privileged)
        recipes_tab.configure_user(user, privileged)
        meals_tab.configure_user(user, privileged)

    window.userSelector.currentIndexChanged.connect(on_user_change)

    def on_tab_change(i):
        tab = window.tabs.widget(i).objectName()
        match tab:
            case "recipesTab":
                recipes_tab.rebuild_ui()
                recipes_tab.configure_user(
                    window.userSelector.currentText(),
                    window.userSelector.currentData()
                )
            case "mealsTab":
                meals_tab.rebuild_ui()
                meals_tab.configure_user(
                    window.userSelector.currentText(),
                    window.userSelector.currentData()
                )
            case "historyTab":
                history_tab.rebuild_ui()
            case "purchasesTab":
                purchases_tab.rebuild_ui()
            case "analyticsTab":
                analytics_tab.rebuild_ui()
            case _:
                inventory_tab.rebuild_ui()
                inventory_tab.configure_user(
                    window.userSelector.currentText(),
                    window.userSelector.currentData()
                )

    window.tabs.setCurrentIndex(0)
    on_tab_change(0)
    on_user_change(0)

    window.tabs.currentChanged.connect(on_tab_change)
    window.shoppingListBtn.clicked.connect(lambda: shopping_list.show(window, dba))
    window.addItemTypeBtn.clicked.connect(lambda: add_item_type.show(window, dba))
    window.addStorageBtn.clicked.connect(lambda: add_storage.show(window, dba))
    window.addLocationBtn.clicked.connect(lambda: add_location.show(window, dba))
    window.addUserBtn.clicked.connect(lambda: add_user.show(window, dba))

    window.show()
