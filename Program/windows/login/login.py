from PyQt5.QtWidgets import QMainWindow, QLineEdit, QAction
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QPropertyAnimation, QRect, QEvent, Qt
from PyQt5.uic import loadUi
import os
from  tools import get_colored_icon
from program import *

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
        self.se_connecter_button.setDefault(True)
        self.utilisateur_lineedit.returnPressed.connect(self.se_connecter_button.click)
        self.mot_de_pass_lineedit.returnPressed.connect(self.se_connecter_button.click)

        # Create toggle action
        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(f"{ASSETS_DIR / "login"}/eye-closed.svg"))
        
        # Add action to password field
        self.mot_de_pass_lineedit.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)
        self.utilisateur_lineedit.setFocus()
        
        # Connect action
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        
        # Set initial state
        self.is_password_hidden = True
        self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Password)

        self.connection_error_label.hide()
    
    def toggle_password_visibility(self):
        if self.is_password_hidden:
            self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon(f"{ASSETS_DIR / "login"}/eye-open.svg"))
        else:
            self.mot_de_pass_lineedit.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon(f"{ASSETS_DIR / "login"}/eye-closed.svg"))
        self.is_password_hidden = not self.is_password_hidden
