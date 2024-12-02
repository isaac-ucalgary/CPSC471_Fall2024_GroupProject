from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt

import view.util as util

class AnalyticsView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

    def rebuild_ui(self):
        usage = self.dba.dynamic_query(
            "History",
            "Select usage statistics"
        )

        self.window.analyticsView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.window.analyticsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.window.analyticsView.setRowCount(len(usage))
        for row, entry in enumerate(usage):
            unit = entry["unit"]
            used = entry["amt_used"]
            wasted = entry["amt_wasted"]
            spent = entry["money_spent"] or 0

            self.window.analyticsView.setItem(row, 0, util.gen_basic_table_cell(entry["item_name"]))
            self.window.analyticsView.setItem(row, 1, util.gen_basic_table_cell(f"{used} {unit}"))
            self.window.analyticsView.setItem(row, 2, util.gen_basic_table_cell(f"{wasted} {unit}"))

            percent_wasted = 100 * wasted / (used + wasted)
            self.window.analyticsView.setItem(row, 3, util.gen_basic_table_cell(f"{percent_wasted:.2f}%"))
            self.window.analyticsView.setItem(row, 4, util.gen_basic_table_cell(f"${spent:.2f}"))
            self.window.analyticsView.setItem(row, 5, util.gen_basic_table_cell(f"${spent * percent_wasted:.2f}"))
