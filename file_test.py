from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableView, QAbstractItemView, QFrame, QLabel
)
import sys


class ProductSelectorWidget(QWidget):
    productSelected = pyqtSignal(dict)  # يرجع المنتج المحدد

    def __init__(self, products=None, parent=None):
        super().__init__(parent)

        self.products = products or []
        self.current_source = None  # الحقل الذي تتم الكتابة فيه الآن
        self.popup_span_widget = None

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("معرف المنتج")
        self.code_edit.setClearButtonEnabled(True)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("وصف المنتج")
        self.desc_edit.setClearButtonEnabled(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.code_edit, 1)
        layout.addWidget(self.desc_edit, 3)

        # popup خارجي يحتوي TableView (non-activating so typing stays in line edits)
        self.popup = QFrame(self, Qt.FramelessWindowHint | Qt.Tool)
        self.popup.setAttribute(Qt.WA_ShowWithoutActivating)
        self.popup.setFrameShape(QFrame.Box)
        self.popup.setLineWidth(1)
        self.popup.setStyleSheet("QFrame { border: 1px solid black; background: white; }")

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.popup.setFocusPolicy(Qt.NoFocus)

        popup_layout.addWidget(self.table)

        self.model = QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels(["المعرف", "الوصف", "ثمن الوحدة"])
        self.table.setModel(self.model)

        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 380)
        self.table.setColumnWidth(2, 120)

        # ربط الأحداث
        self.code_edit.textEdited.connect(lambda text: self.on_text_edited(self.code_edit, text))
        self.desc_edit.textEdited.connect(lambda text: self.on_text_edited(self.desc_edit, text))

        self.code_edit.installEventFilter(self)
        self.desc_edit.installEventFilter(self)
        self.table.installEventFilter(self)

        self.table.doubleClicked.connect(self.choose_current_row)
        self.table.clicked.connect(self.choose_current_row)

    def set_popup_span_widget(self, widget):
        self.popup_span_widget = widget

    # --------------------------
    # البحث / الفلترة
    # --------------------------
    def on_text_edited(self, source_edit, text):
        self.current_source = source_edit
        self.filter_products(text, source_edit)

    def filter_products(self, text, source_edit):
        text = text.strip().lower()
        self.model.setRowCount(0)

        if not text:
            self.popup.hide()
            return

        matches = []
        for product in self.products:
            code = str(product["code"]).lower()
            desc = str(product["description"]).lower()

            # فلترة ذكية: حسب الحقل النشط
            if source_edit is self.code_edit:
                is_match = text in code
            elif source_edit is self.desc_edit:
                is_match = text in desc
            else:
                is_match = text in code or text in desc

            if is_match:
                matches.append(product)

        if not matches:
            self.popup.hide()
            return

        for product in matches:
            row_items = [
                QStandardItem(str(product["code"])),
                QStandardItem(str(product["description"])),
                QStandardItem(f'{product["price"]:.2f}')
            ]

            # تخزين كامل بيانات المنتج داخل أول عنصر في السطر
            row_items[0].setData(product, Qt.UserRole)

            self.model.appendRow(row_items)

        self.table.selectRow(0)
        self.show_popup_below_inputs()

    # --------------------------
    # إظهار الـ popup في نفس الإحداثيات
    # --------------------------
    def show_popup_below_inputs(self):
        # نجعل النافذة تظهر أسفل الـ widget كاملاً، فيبدو الحقلان مترابطين
        global_pos = self.mapToGlobal(QPoint(0, self.height()))
        self.popup.move(global_pos)

        width = self.width()
        if self.popup_span_widget is not None and self.popup_span_widget.isVisible():
            span_right = self.popup_span_widget.mapToGlobal(QPoint(self.popup_span_widget.width(), 0))
            width = max(width, span_right.x() - global_pos.x())

        row_count = self.model.rowCount()
        row_height = 28
        header_height = self.table.horizontalHeader().height()
        max_visible_rows = 8
        visible_rows = min(row_count, max_visible_rows)
        height = header_height + (visible_rows * row_height) + 4

        self.popup.resize(width, height)
        self.table.resize(width, height)
        self.popup.show()
        self.popup.raise_()

        if self.current_source:
            QTimer.singleShot(0, lambda: self.current_source.setFocus(Qt.OtherFocusReason))

    # --------------------------
    # اختيار عنصر
    # --------------------------
    def choose_current_row(self, index=None):
        if index is None:
            index = self.table.currentIndex()

        if not index.isValid():
            return

        row = index.row()
        product_index = self.model.index(row, 0)
        product = self.model.data(product_index, Qt.UserRole)

        if not product:
            return

        self.code_edit.setText(str(product["code"]))
        self.desc_edit.setText(str(product["description"]))

        self.popup.hide()
        if self.current_source:
            QTimer.singleShot(0, lambda: self.current_source.setFocus(Qt.OtherFocusReason))
        self.productSelected.emit(product)

    # --------------------------
    # التنقل بالكيبورد
    # --------------------------
    def eventFilter(self, obj, event):
        if obj in (self.code_edit, self.desc_edit):
            if event.type() == QEvent.KeyPress:
                key = event.key()

                if self.popup.isVisible():
                    if key == Qt.Key_Down:
                        current_row = self.table.currentIndex().row()
                        next_row = min(current_row + 1, self.model.rowCount() - 1)
                        self.table.selectRow(next_row)
                        return True

                    elif key == Qt.Key_Up:
                        current_row = self.table.currentIndex().row()
                        next_row = max(current_row - 1, 0)
                        self.table.selectRow(next_row)
                        return True

                    elif key in (Qt.Key_Return, Qt.Key_Enter):
                        self.choose_current_row()
                        return True

                    elif key == Qt.Key_Escape:
                        self.popup.hide()
                        return True

            elif event.type() == QEvent.FocusOut:
                # لا نغلق مباشرة لتفادي اختفاء popup قبل الضغط عليها
                QApplication.instance().processEvents()

        elif obj == self.table:
            if event.type() == QEvent.KeyPress:
                key = event.key()

                if key in (Qt.Key_Return, Qt.Key_Enter):
                    self.choose_current_row()
                    return True
                elif key == Qt.Key_Escape:
                    self.popup.hide()
                    return True

        return super().eventFilter(obj, event)


class InvoiceLineDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP - سطر فاتورة")

        # بيانات تجريبية
        self.products = [
            {"id": 1, "code": "PRD001", "description": "Armoires de classement 4 tiroirs", "price": 2500.00, "tax": 20},
            {"id": 2, "code": "PRD002", "description": "Bureau en bois massif 160x80", "price": 3200.00, "tax": 20},
            {"id": 3, "code": "PRD003", "description": "Caméra de surveillance IP PoE 4MP", "price": 890.00, "tax": 20},
            {"id": 4, "code": "PRD004", "description": "Chaise de bureau ergonomique", "price": 1250.00, "tax": 20},
            {"id": 5, "code": "PRD005", "description": "Climatiseur split inverter 18000 BTU", "price": 5400.00, "tax": 20},
            {"id": 6, "code": "PRD006", "description": "HP 15s Intel i5 8Go RAM 512Go SSD", "price": 7800.00, "tax": 20},
            {"id": 7, "code": "PRD007", "description": "HP LaserJet Pro MFP M428fdw", "price": 4600.00, "tax": 20},
        ]

        self.selector = ProductSelectorWidget(self.products)

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("PU HT")
        self.price_edit.setReadOnly(True)
        self.selector.set_popup_span_widget(self.price_edit)

        product_label = QLabel("Produit :")

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        row_layout.addWidget(product_label)
        row_layout.addWidget(self.selector, 1)
        row_layout.addWidget(self.price_edit)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(row_layout)

        self.selector.productSelected.connect(self.on_product_selected)

    def on_product_selected(self, product):
        self.price_edit.setText(f'{product["price"]:.2f}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = InvoiceLineDemo()
    w.resize(800, 140)
    w.show()
    sys.exit(app.exec_())