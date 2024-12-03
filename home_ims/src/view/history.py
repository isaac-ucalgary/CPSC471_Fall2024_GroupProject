from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QBrush, QColor

import view.util as util

WASTED_BRUSH = QBrush(Qt.BrushStyle.SolidPattern)
WASTED_BRUSH.setColor(QColor(241, 208, 205))

USED_BRUSH = QBrush(Qt.BrushStyle.SolidPattern)
USED_BRUSH.setColor(QColor(217, 231, 214))

NO_USER_BRUSH = QBrush(Qt.BrushStyle.BDiagPattern)
NO_USER_BRUSH.setColor(Qt.GlobalColor.black)

class HistoryView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba
    
    def rebuild_ui(self):
        records = self.dba.dynamic_query("History", "Select history records")

        proxy = util.Sorting(self.window.analyticsView)
        proxy.setSourceModel(Model(records))

        self.window.historyView.setModel(proxy)
        self.window.historyView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.window.historyView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

class Model(QAbstractTableModel):
    def __init__(self, records):
        super().__init__()
        self.records = records

    def data(self, index, role):
        entry = self.records[index.row()]
        match index.column(), role:
            case 0, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return entry["item_name"]

            case 1, Qt.ItemDataRole.DisplayRole:
                return util.format_quantity(entry["quantity"], entry["unit"])
            case 1, Qt.ItemDataRole.UserRole:
                return (entry["unit"], entry["quantity"])

            case 2, Qt.ItemDataRole.DisplayRole:
                return util.format_datetime(entry["timestamp"])
            case 2, Qt.ItemDataRole.UserRole:
                return entry["timestamp"]

            case 3, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return "Wasted" if entry["wasted"] else "Used"
            case 3, Qt.ItemDataRole.BackgroundRole:
                return WASTED_BRUSH if entry["wasted"] else USED_BRUSH

            case 4, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return entry["user_name"]
            case 4, Qt.ItemDataRole.BackgroundRole:
                if entry["user_name"] is None:
                    return NO_USER_BRUSH
                

    def rowCount(self, index):
        return len(self.records)

    def columnCount(self, index):
        return 5
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            match section:
                case 0:
                    return "Item Type"
                case 1:
                    return "Quantity"
                case 2:
                    return "Date Recorded"
                case 3:
                    return "Outcome"
                case 4:
                    return "User"

