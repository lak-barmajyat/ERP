import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from program.windows.login import LoginWindow
from program.windows.dashboard import DashboardWindow, dashboard_setup
from program.windows.nouveau_doc import NouveauDocWindow, nouveau_doc_setup
from program.themes.theme_manager import ThemeManager
from PyQt5.QtGui import QFontDatabase


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()
    nouveau_doc_setup(window)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
