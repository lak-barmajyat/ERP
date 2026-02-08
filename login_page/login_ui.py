import sys
from os import getenv
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation, QRect, QEvent, Qt
from PyQt5.uic import loadUi
import mysql.connector


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('login_screen.ui', self)

        self.annuler_button.clicked.connect(self.close)
        self.se_connecter_button.clicked.connect(self.close)

        # Create toggle action
        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon("icons/eye-closed.svg"))
        
        # Add action to password field
        self.password_lineedit.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)
        
        # Connect action
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        
        # Set initial state
        self.is_password_hidden = True
        self.password_lineedit.setEchoMode(QLineEdit.Password)
    
    def toggle_password_visibility(self):
        if self.is_password_hidden:
            self.password_lineedit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon("icons/eye-open.svg"))
        else:
            self.password_lineedit.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon("icons/eye-closed.svg"))
        self.is_password_hidden = not self.is_password_hidden
