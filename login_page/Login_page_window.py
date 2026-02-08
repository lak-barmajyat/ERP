import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QPropertyAnimation, QRect, QEvent, Qt
from PyQt5.uic import loadUi
import mysql.connector

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('login_screen.ui', self)

        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.close)

# conn = mysql.connector.connect(
#     host="DB_HOST",
#     user="DB_USER",
#     password="DB_PASSWORD",
#     database="DB_NAME",
#     charset="DB_CHARSET"
# )
# cursor = conn.cursor()

# cursor.execute("SHOW TABLES")

# for table in cursor:
#     print(table)

# cursor.close()
# conn.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowFlags(Qt.FramelessWindowHint)
    window.setAttribute(Qt.WA_TranslucentBackground)
    window.show()
    sys.exit(app.exec_())