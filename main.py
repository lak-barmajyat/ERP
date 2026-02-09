import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from program.windows.login.login import LoginWindow
from program.windows.dashboard.dashboard import DashboardWindow
from program.services.db_connection import get_db_connection, close_db_connection


def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    #window.setWindowFlags(Qt.FramelessWindowHint)
    #window.setAttribute(Qt.WA_TranslucentBackground)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    connect, cursor = get_db_connection()
    
    main()

    close_db_connection(connect, cursor)