import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import os


def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super(DashboardWindow, self).__init__()
        loadUi(resource_path("dashboard.ui"), self)


def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()