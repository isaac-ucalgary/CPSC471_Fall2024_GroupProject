from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_recipe.ui"))
entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("popup", "recipe_ingredient.ui"))

def show(window, dba, refresh):
    food_types = dba.dynamic_query("Food", "Select food type")
    if not food_types.is_success():
        util.open_error_dialog(window)
        return

    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        def add_ingredient():
            entry_widget = entry_base_tpl()
            entry_form = entry_form_tpl()
            entry_form.setupUi(entry_widget)
            
            for t in food_types.get_data_list():
                entry_form.itemSelector.addItem(t["name"], t["unit"])

            def on_item_change(i):
                unit = entry_form.itemSelector.itemData(i)
                entry_form.unit.setVisible(bool(unit))
                entry_form.unit.setText(unit)

            on_item_change(0)

            entry_form.itemSelector.currentIndexChanged.connect(on_item_change)
            entry_form.removeBtn.clicked.connect(entry_widget.deleteLater)

            form.ingredients.layout().addWidget(entry_widget)
        
        def create():
            entries = form.ingredients.findChildren(QWidget, "RecipeIngredient", Qt.FindChildOption.FindDirectChildrenOnly)

            recipe_name = form.recipeNameInput.text()
            if not recipe_name:
                util.open_error_dialog(window, "No recipe name given.")
                return

            ingredients = []
            for e in entries:
                try:
                    item_name = e.findChild(QWidget, "itemSelector", Qt.FindChildOption.FindDirectChildrenOnly).currentText()
                    quantity = float(e.findChild(QWidget, "quantityInput", Qt.FindChildOption.FindDirectChildrenOnly).text())
                    if quantity <= 0:
                        raise ValueError("Quantity not positive.")

                    ingredients.append((item_name, quantity))
                except ValueError:
                    util.open_error_dialog(window, "Invalid quantity.")
                    return

            if not ingredients:
                util.open_error_dialog(window, "No ingredients given.")
                return

            add = dba.add_recipe(recipe_name, ingredients)
            if not add.is_success():
                print(add.get_exception())
                util.open_error_dialog(window)
                return

            close_dlg()
            refresh()

        form.scrollArea.horizontalScrollBar().setEnabled(False)
        form.addIngredientBtn.clicked.connect(add_ingredient)
        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)

        return widget

    util.open_dialog(window, gen_widget)
