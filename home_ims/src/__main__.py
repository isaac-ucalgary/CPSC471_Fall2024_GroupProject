from PyQt6 import QtWidgets
import sys

from Database import *
import view

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    db = Database()
    if db.connect():
        # Build the database if it doesn't exist
        db.build_database()

        dba = db.db_actions
        view.show_window(dba)
        app.exec()
    else:
        print("Could not connect to database. Exiting.")
