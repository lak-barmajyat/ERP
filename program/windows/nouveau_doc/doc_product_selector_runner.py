import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class DocProductSelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).with_name("doc_product_selector.ui")
        uic.loadUi(str(ui_path), self)


def main() -> int:
    app = QApplication(sys.argv)
    window = DocProductSelectorWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
