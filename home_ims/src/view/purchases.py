from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt, QAbstractTableModel
from datetime import datetime

import view.util as util

class PurchasesView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

    def rebuild_ui(self):
        records = self.dba.dynamic_query("Purchase", "Select purchases")
        proxy = util.Sorting(self.window.analyticsView)
        proxy.setSourceModel(Model(records))

        self.window.purchasesView.setModel(proxy)
        self.window.purchasesView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.window.purchasesView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

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

            case 3, Qt.ItemDataRole.DisplayRole:
                price = entry["price"]
                return f"{price:.2f}"
            case 3, Qt.ItemDataRole.UserRole:
                return entry["price"]

            case 4, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return entry["store"]

            case 5, Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.UserRole:
                return entry["parent_name"]

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
                    return "Quantity"
                case 2:
                    return "Date Recorded"
                case 3:
                    return "Price"
                case 4:
                    return "Store"
                case 5:
                    return "Buyer"
