from PyQt6 import QtWidgets
import sys

from Database import *
import view

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    db = Database()
    if db.connect():
        # db.build_database() # TODO: This currently closes my connection. Should I not be using this in the application?
        dba = Database.DB_Actions(db)
        view.show_window(dba)
        app.exec()
    else:
        print("Could not connect to database. Exiting.")
