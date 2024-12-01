from PyQt6 import QtWidgets
import sys

from Database import *
import view

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    db = Database()
    db.connect()
    # db.build_database()
    dba = Database.DB_Actions(db)

    view.show_window(dba)

    app.exec()
