from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt

import view.util as util

class HistoryView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba
    
    def rebuild_ui(self):
        hist = self.dba.dynamic_query("History", "Select history records")

        self.window.historyView.setRowCount(len(hist))
        for row, entry in enumerate(hist):
            self.window.historyView.setItem(row, 0, _gen_basic_cell(entry["item_name"]))
            self.window.historyView.setItem(row, 1, _gen_basic_cell(util.format_quantity(entry["quantity"], entry["unit"])))
            self.window.historyView.setItem(row, 2, _gen_basic_cell(util.format_datetime(entry["date_used"])))

            outcome = QTableWidgetItem()
            user = QTableWidgetItem()

            if entry["wasted"]:
                obg = QBrush(Qt.BrushStyle.SolidPattern)
                obg.setColor(QColor(241, 208, 205))
                outcome.setBackground(obg)
                outcome.setText("Wasted")

                ubg = QBrush(Qt.BrushStyle.BDiagPattern)
                ubg.setColor(Qt.GlobalColor.black)
                user.setBackground(ubg)
            else:
                bg = QBrush(Qt.BrushStyle.SolidPattern)
                bg.setColor(QColor(217, 231, 214))
                outcome.setBackground(bg)
                outcome.setText("Used")

                user.setText(entry["user_name"])

            self.window.historyView.setItem(row, 3, outcome)
            self.window.historyView.setItem(row, 4, user)

def _gen_basic_cell(text):
    cell = QTableWidgetItem()
    cell.setText(text)
    return cell