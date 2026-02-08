import sys
from os import getenv
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import mysql.connector

from login_page.login_ui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowFlags(Qt.FramelessWindowHint)
    window.setAttribute(Qt.WA_TranslucentBackground)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    load_dotenv("../.env")
    connect = mysql.connector.connect(
        host=getenv("DB_HOST"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        database=getenv("DB_NAME")
    )
    cursor = connect.cursor()
    main()

    cursor.close()
    connect.close()