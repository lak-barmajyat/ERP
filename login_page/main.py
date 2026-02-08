import sys
from os import getenv
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QPropertyAnimation, QRect, QEvent, Qt
from PyQt5.uic import loadUi
import mysql.connector

def set_mysql_connection():
    try:
        print("Attempting to connect to MySQL database...")
        connect = mysql.connector.connect(
            host=getenv("DB_HOST"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            database=getenv("DB_NAME")
            # charset=getenv("DB_CHARSET")
        )
        print("Connected to MySQL database successfully!")
        cursor = connect.cursor()
        return connect, cursor
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        sys.exit(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        print("Initializing MainWindow...")
        loadUi('login_screen.ui', self)

        self.annuler_button.clicked.connect(self.close)
        self.oublie_mot_de_passe_button.clicked.connect(self.close)
        self.se_connecter_button.clicked.connect(self.close)


if __name__ == '__main__':
    load_dotenv("../.env")
    # connect, cursor = set_mysql_connection()
    print(getenv("DB_HOST"))
    
    try:
        # sql = """
        # INSERT INTO `utilisateurs` (`nom_utilisateur`, `mot_de_passe_hash`, `role`)
        # VALUES (%s, %s, %s)
        # """
        # values = ("Mossabe", "Hello123", "admin")
        # cursor.execute(sql, values)
        # connect.commit()
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.setAttribute(Qt.WA_TranslucentBackground)
        window.show()
        sys.exit(app.exec_())
    finally:
        cursor.close()
        connect.close()
