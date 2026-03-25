from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableView, QAbstractItemView, QFrame
)


class ProductSelectorWidget(QWidget):
    productSelected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.products = []
        self.current_source = None
        self.popup_span_widget = None

        # --------------------------
        # Inputs
        # --------------------------
        self.code_edit = QLineEdit(self)
        self.code_edit.setPlaceholderText("Reference")
        self.code_edit.setClearButtonEnabled(True)

        self.desc_edit = QLineEdit(self)
        self.desc_edit.setPlaceholderText("Designation")
        self.desc_edit.setClearButtonEnabled(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.code_edit, 1)
        layout.addWidget(self.desc_edit, 3)

        # --------------------------
        # Popup
        # --------------------------
        self.popup = QFrame(self, Qt.FramelessWindowHint | Qt.Tool)
        self.popup.setAttribute(Qt.WA_ShowWithoutActivating)
        self.popup.setFocusPolicy(Qt.NoFocus)
        self.popup.setFrameShape(QFrame.Box)
        self.popup.setStyleSheet("background:white; border:1px solid #d1d5db;")

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView(self.popup)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().hide()
        self.table.setShowGrid(False)

        popup_layout.addWidget(self.table)

        # --------------------------
        # Model
        # --------------------------
        self.model = QStandardItemModel(0, 3, self)
        self.table.setModel(self.model)

        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 380)
        self.table.setColumnWidth(2, 120)

        # --------------------------
        # Events
        # --------------------------
        self.code_edit.textEdited.connect(
            lambda text: self.on_text_edited(self.code_edit, text)
        )
        self.desc_edit.textEdited.connect(
            lambda text: self.on_text_edited(self.desc_edit, text)
        )

        self.code_edit.installEventFilter(self)
        self.desc_edit.installEventFilter(self)
        self.table.installEventFilter(self)

        self.table.clicked.connect(self.choose_current_row)

    # ==========================
    # API
    # ==========================
    def set_products(self, products):
        self.products = products or []

    def set_popup_span_widget(self, widget):
        self.popup_span_widget = widget

    # ==========================
    # Search
    # ==========================
    def on_text_edited(self, source, text):
        self.current_source = source
        self.filter_products(text, source)

    def filter_products(self, text, source):
        text = text.strip().lower()
        self.model.setRowCount(0)

        if not text:
            self.popup.hide()
            return

        matches = []

        for p in self.products:
            code = str(p["code"]).lower()
            desc = str(p["description"]).lower()

            if source is self.code_edit:
                ok = text in code
            else:
                ok = text in code or text in desc

            if ok:
                matches.append(p)

        if not matches:
            self.popup.hide()
            return

        for p in matches:
            items = [
                QStandardItem(p["code"]),
                QStandardItem(p["description"]),
                QStandardItem(f'{p["price"]:.2f}')
            ]
            items[0].setData(p, Qt.UserRole)
            self.model.appendRow(items)

        self.table.selectRow(0)
        self.show_popup()

    # ==========================
    # Popup
    # ==========================
    def show_popup(self):
        pos = self.mapToGlobal(QPoint(0, self.height()))
        self.popup.move(pos)

        width = self.width()
        if self.popup_span_widget:
            span = self.popup_span_widget.mapToGlobal(
                QPoint(self.popup_span_widget.width(), 0)
            )
            width = max(width, span.x() - pos.x())

        rows = min(self.model.rowCount(), 8)
        height = rows * 28 + 4

        self.popup.resize(width, height)
        self.popup.show()

        if self.current_source:
            QTimer.singleShot(0, lambda: self.current_source.setFocus())

    # ==========================
    # Select
    # ==========================
    def choose_current_row(self, index=None):
        if index is None:
            index = self.table.currentIndex()

        if not index.isValid():
            return

        product = self.model.data(
            self.model.index(index.row(), 0),
            Qt.UserRole
        )

        if not product:
            return

        self.code_edit.setText(product["code"])
        self.desc_edit.setText(product["description"])

        self.popup.hide()
        self.productSelected.emit(product)

    # ==========================
    # Keyboard
    # ==========================
    def eventFilter(self, obj, event):
        if obj in (self.code_edit, self.desc_edit):
            if event.type() == QEvent.KeyPress:
                if self.popup.isVisible():

                    if event.key() == Qt.Key_Down:
                        r = self.table.currentIndex().row()
                        self.table.selectRow(min(r + 1, self.model.rowCount() - 1))
                        return True

                    if event.key() == Qt.Key_Up:
                        r = self.table.currentIndex().row()
                        self.table.selectRow(max(r - 1, 0))
                        return True

                    if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                        self.choose_current_row()
                        return True

        return super().eventFilter(obj, event)

    def clear_selection(self):
        self.code_edit.clear()
        self.desc_edit.clear()
        self.popup.hide()

    def set_product(self, product):
        self.products = [product] if product else []

    def set_popup_span_widget(self, widget):
        self.popup_span_widget = widget
