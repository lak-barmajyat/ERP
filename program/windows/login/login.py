from PyQt5.QtWidgets import QMainWindow, QLineEdit, QAction
from PyQt5.QtGui import QIcon, QColor, QGuiApplication
from PyQt5.QtCore import QPropertyAnimation, QRect, QEvent, Qt, QTimer
from PyQt5.uic import loadUi
import os
from  tools import get_colored_icon
from program.services.paths import ASSETS_LOGIN
from program.windows.login.login_funcs import check_user

def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)




class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi(resource_path("login.ui"), self)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.annuler_button.clicked.connect(self.close)
        self.se_connecter_button.clicked.connect(lambda: check_user(self))
        self.se_connecter_button.setFocus(True)
        self.utilisateur_lineedit.returnPressed.connect(self.mot_de_pass_lineedit.setFocus)
        self.mot_de_pass_lineedit.returnPressed.connect(self.se_connecter_button.click)

        # Create toggle action
        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(f"{ASSETS_LOGIN}/eye-closed.svg"))
        
        # Add action to password field
        self.mot_de_pass_lineedit.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)
        self.utilisateur_lineedit.setFocus()
        
        # Connect action
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        
        # Set initial state
        self.is_password_hidden = True
        self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Password)

        self.connection_error_label.hide()

        self.show()
        QTimer.singleShot(0, self.center_on_screen)  # center after show
    
    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return

        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()

        x = screen_geometry.x() + (screen_geometry.width() - window_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_geometry.height()) // 2

        self.move(x, y)

    def toggle_password_visibility(self):
        if self.is_password_hidden:
            self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon(f"{ASSETS_LOGIN}/eye-open.svg"))
        else:
            self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon(f"{ASSETS_LOGIN}/eye-closed.svg"))
        self.is_password_hidden = not self.is_password_hidden
