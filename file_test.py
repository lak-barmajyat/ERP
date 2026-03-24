import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMenu, QVBoxLayout, QWidget, QAction
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار QMenu مع زوايا مدورة")
        self.setGeometry(200, 200, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.button = QPushButton("إظهار القائمة")
        self.button.clicked.connect(self.show_menu)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        # تطبيق الـ QSS على التطبيق بأكمله (أو يمكن تطبيقه على القائمة فقط)
        self.setup_stylesheet()

    def setup_stylesheet(self):
        """تطبيق QSS الذي يحافظ على الزوايا المدورة للقائمة."""
        qss = """
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 3px;
            font: 600 9pt "Overpass";
            color: #374151;
            /* منع الخلفية من التجاوز خارج الحدود */
            background-clip: padding;
            /* إزالة أي هوامش إضافية */
            margin: 0px;
        }
        QMenu::item {
            padding: 3px 8px;
            border-radius: 6px;
            min-width: 180px;
            /* التأكد من أن العنصر لا يضيف خلفية خارج حدوده */
            background-clip: padding;
        }
        QMenu::item:selected {
            background-color: #eef4ff;
            color: #135bec;
        }
        QMenu::separator {
            height: 1px;
            margin: 6px 8px;
            background: #e5e7eb;
        }
        """
        self.setStyleSheet(qss)

    def show_menu(self):
        """إنشاء وعرض القائمة."""
        menu = QMenu(self)

        action1 = QAction("خيار أول", self)
        action2 = QAction("خيار ثاني", self)
        action3 = QAction("خيار ثالث", self)

        menu.addAction(action1)
        menu.addAction(action2)
        menu.addSeparator()
        menu.addAction(action3)

        # عرض القائمة بجانب الزر
        menu.exec_(self.button.mapToGlobal(self.button.rect().bottomLeft()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())