import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from program.windows.login.login import LoginWindow
from program.windows.dashboard.dashboard import DashboardWindow
from program.windows.clients.add_facture import ClientsFacturesWindow
from program.services.db_connection import get_db_connection, close_db_connection
from theme_manager import ThemeManager
from PyQt5.QtGui import QFontDatabase


def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
<<<<<<< HEAD
    theme_manager = ThemeManager(app)
    theme_manager.load_theme("dark")
=======
>>>>>>> 48c07e308d1981e1431a1fce68946be8d57ae698
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    connect, cursor = get_db_connection()
    
    main()

    close_db_connection(connect, cursor)