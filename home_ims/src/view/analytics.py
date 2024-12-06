from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt, QAbstractTableModel

from view import util

class AnalyticsView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

    def rebuild_ui(self):
        records = self.dba.dynamic_query("History", "Select usage statistics")

        proxy = util.Sorting(self.window.analyticsView)
        proxy.setSourceModel(Model(records))

        self.window.analyticsView.setModel(proxy)
        self.window.analyticsView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.window.analyticsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

class Model(QAbstractTableModel):
    def __init__(self, records):
        super().__init__()
        self.records = records

    def data(self, index, role):
        entry = self.records[index.row()]

        unit = entry["unit"]
        used = entry["amt_used"]
        wasted = entry["amt_wasted"]
        spent = entry["money_spent"]
        fraction_wasted = wasted / (used + wasted)

        match index.column(), role:
            case 0, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return entry["item_name"]

            case 1, Qt.ItemDataRole.DisplayRole:
                return util.format_quantity(used, unit)
            case 1, Qt.ItemDataRole.UserRole:
                return (used, unit)

            case 2, Qt.ItemDataRole.DisplayRole:
                return util.format_quantity(wasted, unit)
            case 2, Qt.ItemDataRole.UserRole:
                return (wasted, unit)

            case 3, Qt.ItemDataRole.DisplayRole:
                return f"{100 * fraction_wasted:.2f}%"
            case 3, Qt.ItemDataRole.UserRole:
                return fraction_wasted

            case 4, Qt.ItemDataRole.DisplayRole:
                return f"${spent:.2f}"
            case 4, Qt.ItemDataRole.UserRole:
                return spent

            case 5, Qt.ItemDataRole.DisplayRole:
                return f"${spent * fraction_wasted:.2f}"
            case 5, Qt.ItemDataRole.UserRole:
                return spent * fraction_wasted

    def rowCount(self, index):
        return len(self.records)

    def columnCount(self, index):
        return 6
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            match section:
                case 0:
                    return "Item Type"
                case 1:
                    return "Amount Used"
                case 2:
                    return "Amount Wasted"
                case 3:
                    return "% Wasted"
                case 4:
                    return "Money Spent"
                case 5:
                    return "Money Wasted"
