import os
from PyQt6.QtWidgets import QTableWidgetItem

root = os.path.dirname(__file__)

def get_ui_path(filename):
    return os.path.join(root, "ui", filename)

def format_quantity(quantity, unit):
    return f"{quantity:.1f} {unit}"

def format_date(timestamp):
    return timestamp.strftime("%-d %b, %Y")

def format_datetime(timestamp):
    return timestamp.strftime("%I:%M:%S %p, %-d %b, %Y")

def gen_basic_table_cell(text):
    cell = QTableWidgetItem()
    cell.setText(text)
    return cell
