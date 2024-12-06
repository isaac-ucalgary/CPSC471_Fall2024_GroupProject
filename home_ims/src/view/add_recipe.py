from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from view import util

form_tpl, base_tpl = uic.loadUiType(util.get_ui_path("popup", "add_recipe.ui"))
entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("popup", "recipe_ingredient.ui"))

def show(window, dba):
    def gen_widget(close_dlg):
        widget = base_tpl()
        form = form_tpl()
        form.setupUi(widget)

        def add_ingredient():
            entry_widget = entry_base_tpl()
            entry_form = entry_form_tpl()
            entry_form.setupUi(entry_widget)
            form.ingredients.layout().addWidget(entry_widget)
        
        def create():
            close_dlg()

        form.addIngredientBtn.clicked.connect(add_ingredient)
        form.cancelBtn.clicked.connect(close_dlg)
        form.addBtn.clicked.connect(create)

        return widget

    util.open_dialog(window, gen_widget)
