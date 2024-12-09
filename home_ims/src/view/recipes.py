from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import uic

import view.add_recipe as add_recipe
from view import util

entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("recipe_entry.ui"))
schedule_form_tpl, schedule_base_tpl = uic.loadUiType(util.get_ui_path("popup", "schedule_meal.ui"))
remove_form_tpl, remove_base_tpl = uic.loadUiType(util.get_ui_path("popup", "delete_recipe.ui"))

class RecipesView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

        self.window.addRecipeBtn.clicked.connect(
            lambda: add_recipe.show(self.window, self.dba, self.update_view)
        )
        self.window.refreshRecipesBtn.clicked.connect(self.update_view)

    def rebuild_ui(self):
        self.window.recipeSearch.clear()
        self.window.searchByName.setChecked(True)
        self.update_view()

    def update_view(self):
        recipes = self.dba.dynamic_query(
            "Recipe",
            "View recipes",
            recipe_name="%"
        )

        if not recipes.is_success():
            util.open_error_dialog(self.window)
            return

        c_layout = QVBoxLayout()
        container = QWidget()
        container.setProperty("nobackground", True)
        container.setLayout(c_layout)

        for entry in recipes.get_data_list():
            widget = entry_base_tpl()
            form = entry_form_tpl()
            form.setupUi(widget)

            form.recipeName.setText(entry["recipe_name"])
            form.scheduleBtn.clicked.connect(lambda _, e=entry: self.schedule_dialog(e))
            form.removeBtn.clicked.connect(lambda _, e=entry: self.remove_dialog(e))

            c_layout.addWidget(widget)
        
        c_layout.addStretch()

        self.window.recipesView.setWidget(container)

    def configure_user(self, user, privileged):
        self.window.addRecipeBtn.setEnabled(privileged)

    def schedule_dialog(self, entry):
        def gen_dialog(close_dlg):
            widget = schedule_base_tpl()
            form = schedule_form_tpl()
            form.setupUi(widget)

            def schedule():
                result = self.dba.dynamic_query(
                    "MealSchedule",
                    "Schedule a meal",
                    recipe_name=entry["recipe_name"],
                    timestamp=form.dateInput.dateTime().toPyDateTime(),
                    meal_type=form.mealTypeInput.text()
                )
                if not result.is_success():
                    util.open_error_dialog(self.window)
                    return

                self.update_view()
                close_dlg()

            form.recipe.setText(entry["recipe_name"])
            form.cancelBtn.clicked.connect(close_dlg)
            form.scheduleBtn.clicked.connect(schedule)

            return widget

        util.open_dialog(self.window, gen_dialog)           
    
    def remove_dialog(self, entry):
        def gen_dialog(close_dlg):
            widget = remove_base_tpl()
            form = remove_form_tpl()
            form.setupUi(widget)

            def delete():
                result = self.dba.dynamic_query(
                    "Recipe",
                    "Delete recipe",
                    recipe_name=entry["recipe_name"]
                )
                if not result.is_success():
                    util.open_error_dialog(self.window)
                    return
                
                self.update_view()
                close_dlg()
            
            form.recipe.setText(entry["recipe_name"])
            form.cancelBtn.clicked.connect(close_dlg)
            form.deleteBtn.clicked.connect(delete)

            return widget

        util.open_dialog(self.window, gen_dialog)
