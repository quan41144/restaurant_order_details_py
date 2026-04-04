import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication

from app.database.db import Database
from app.UI.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    db = Database()
    window = MainWindow(db)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()