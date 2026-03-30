from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableView, QAbstractItemView, QFrame, QHeaderView
)
from program.themes.shared_input_popup_style import apply_lineedit_style, apply_table_popup_style


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
        apply_lineedit_style(self.code_edit)

        self.desc_edit = QLineEdit(self)
        self.desc_edit.setPlaceholderText("Designation")
        apply_lineedit_style(self.desc_edit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.code_edit, 1)
        layout.addWidget(self.desc_edit, 3)

        # --------------------------
        # Popup
        # --------------------------
        self.popup = QFrame(self, Qt.FramelessWindowHint | Qt.Tool)
        self.popup.setAttribute(Qt.WA_ShowWithoutActivating)
        self.popup.setFocusPolicy(Qt.NoFocus)
        self.popup.setFrameShape(QFrame.Box)
        self.popup.setStyleSheet("background: transparent; border: none;")

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView(self.popup)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setMouseTracking(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        apply_table_popup_style(self.table, row_height=30)

        popup_layout.addWidget(self.table)

        # --------------------------
        # Model
        # --------------------------
        self.model = QStandardItemModel(0, 3, self)
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

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

        self.table.entered.connect(self._on_table_row_hovered)
        self.table.clicked.connect(self.choose_current_row)

        # Ensure popup is cleaned up with parent/window lifecycle.
        self.destroyed.connect(lambda *_: self._hide_popup_safely())
        QTimer.singleShot(0, self._install_window_event_filter)

    def _install_window_event_filter(self):
        top = self.window()
        if top is not None and top is not self:
            top.installEventFilter(self)

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _point_in_widget(self, widget, global_pos):
        if widget is None or not widget.isVisible():
            return False
        local_pos = widget.mapFromGlobal(global_pos)
        return widget.rect().contains(local_pos)

    def _is_inside_selector_or_popup(self, global_pos):
        # Keep popup open when user interacts with selector inputs or popup/table.
        if self._point_in_widget(self, global_pos):
            return True
        if self._point_in_widget(self.popup, global_pos):
            return True
        if self._point_in_widget(self.table, global_pos):
            return True
        viewport = self.table.viewport() if self.table else None
        if viewport is not None and self._point_in_widget(viewport, global_pos):
            return True
        return False

    def _hide_popup_safely(self):
        try:
            self.popup.hide()
        except RuntimeError:
            pass

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

    def _on_table_row_hovered(self, index):
        if not index.isValid():
            return
        self.table.selectRow(index.row())

    # ==========================
    # Keyboard
    # ==========================
    def eventFilter(self, obj, event):
        if obj is self.window() and event.type() in (QEvent.Close, QEvent.Hide):
            self._hide_popup_safely()
            return super().eventFilter(obj, event)

        if self.popup.isVisible() and event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
            global_pos_getter = getattr(event, "globalPos", None)
            if callable(global_pos_getter):
                if not self._is_inside_selector_or_popup(global_pos_getter()):
                    self.popup.hide()

        if self.popup.isVisible() and event.type() == QEvent.WindowDeactivate:
            self.popup.hide()

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

                    if event.key() == Qt.Key_Escape:
                        self.popup.hide()
                        return True

        return super().eventFilter(obj, event)

    def hideEvent(self, event):
        self._hide_popup_safely()
        super().hideEvent(event)

    def closeEvent(self, event):
        self._hide_popup_safely()
        super().closeEvent(event)

    def clear_selection(self):
        self.code_edit.clear()
        self.desc_edit.clear()
        self.popup.hide()

    def set_product(self, product):
        self.products = [product] if product else []

    def set_popup_span_widget(self, widget):
        self.popup_span_widget = widget
