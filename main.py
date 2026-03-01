import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from program.windows.login.login import LoginWindow
from program.windows.dashboard.dashboard import DashboardWindow
from program.windows.nouveau_doc.nouveau_doc import NouveauDocWindow
from program.windows.liste_ventes.liste_ventes import SalesDocumentsWindow
from program.themes.theme_manager import ThemeManager
from PyQt5.QtGui import QFontDatabase


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()

    #theme_manager = ThemeManager(app)
    #theme_manager.load_theme("light")  # Load default theme/

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
