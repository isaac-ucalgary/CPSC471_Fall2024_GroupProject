from PyQt6.QtWidgets import QWidget, QVBoxLayout, QAbstractButton
from PyQt6 import uic
import datetime as dt

from view import util

entry_form_tpl, entry_base_tpl = uic.loadUiType(util.get_ui_path("meal_entry.ui"))

class MealsView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

    def rebuild_ui(self):
        self.update_view()

    def update_view(self):
        meals = self.dba.dynamic_query(
            "MealSchedule",
            "Select meals",
            recipe_name="%",
            timestamp_from=dt.datetime.min,
            timestamp_to=dt.datetime.max,
            location_name="%",
            meal_type="%"
        )

        if not meals.is_success():
            util.open_error_dialog(self.window)
            return
        
        c_layout = QVBoxLayout()
        container = QWidget()
        container.setProperty("nobackground", True)
        container.setLayout(c_layout)

        for entry in meals.get_data_list():
            widget = entry_base_tpl()
            form = entry_form_tpl()
            form.setupUi(widget)

            form.recipe.setText(entry["recipe_name"])
            form.scheduleDate.setText("Scheduled for " + util.format_date(entry["timestamp"]))
            form.consumeBtn.clicked.connect(lambda _, e=entry: self.consume_meal(e))
            form.removeBtn.clicked.connect(lambda _, e=entry: self.remove_meal(e))

            c_layout.addWidget(widget)
        
        c_layout.addStretch()

        self.window.mealsView.setWidget(container)
    
    def configure_user(self, user, privileged):
        self.current_user = user
        self.window.addRecipeBtn.setEnabled(privileged)
        for widget in self.window.mealsView.widget().findChildren(QAbstractButton):
            widget.setEnabled(privileged)

    def consume_meal(self, entry):
        result = self.dba.consume_meal(
            entry["recipe_name"],
            entry["timestamp"],
            self.current_user
        )

        if not result.is_success():
            util.open_error_dialog(self.window)
            return

        self.update_view()

    def remove_meal(self, entry):
        result = self.dba.dynamic_query(
            "MealSchedule",
            "Delete a meal",
            recipe_name=entry["recipe_name"],
            timestamp=entry["timestamp"]
        )

        if not result.is_success():
            util.open_error_dialog(self.window)
            return
        
        self.update_view()
