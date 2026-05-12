
"""
Reusable ERP Table Widget for PyQt5
Architecture: QTableView + QAbstractTableModel (no QTableWidget)
"""

import sys
import math
import random

from PyQt5.QtWidgets import (
    QTableView, QAbstractItemView, QHeaderView, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMenu, QStyle, QStyleOptionButton, QStyledItemDelegate,
    QApplication, QFrame, QAction, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, pyqtSignal, QTimer,
    QEvent, QRect, QSize
)
from PyQt5.QtGui import QPainter, QColor, QFont, QPen


# ═══════════════════════════════════════════════════════════════════════
#  TABLE MODEL
# ═══════════════════════════════════════════════════════════════════════

class ErpTableModel(QAbstractTableModel):
    """
    Custom table model for ERP data.
    Column 0 is always the checkbox (bulk-selection) column.
    Data columns start from index 1.
    """

    def __init__(self, columns_config=None, parent=None):
        super().__init__(parent)
        self._columns = columns_config or []
        self._data = []
        self._checked_rows = set()
        self._sort_mapping = []
        self._sort_column = -1
        self._sort_order = Qt.AscendingOrder
        self._total_count = 0
        self._rebuild_sort_mapping()

    def set_columns(self, columns_config):
        self.beginResetModel()
        self._columns = columns_config or []
        self._checked_rows.clear()
        self._rebuild_sort_mapping()
        self.endResetModel()

    def set_data(self, data, total_count=0):
        self.beginResetModel()
        self._data = list(data) if data else []
        self._total_count = total_count if total_count > 0 else len(self._data)
        self._checked_rows.clear()
        self._rebuild_sort_mapping()
        self.endResetModel()

    def append_data(self, new_data):
        if not new_data:
            return

        old_persistent = self.persistentIndexList()
        old_mapping = list(self._sort_mapping)

        self.layoutAboutToBeChanged.emit()

        self._data.extend(new_data)
        self._total_count = max(self._total_count, len(self._data))
        self._rebuild_sort_mapping()

        new_indexes = []
        for idx in old_persistent:
            data_row = old_mapping[idx.row()] if idx.row() < len(old_mapping) else -1
            if data_row >= 0:
                try:
                    new_row = self._sort_mapping.index(data_row)
                except ValueError:
                    new_row = idx.row()
            else:
                new_row = idx.row()
            new_indexes.append(self.index(new_row, idx.column()))

        self.changePersistentIndexList(old_persistent, new_indexes)
        self.layoutChanged.emit()

    def clear(self):
        self.set_data([], 0)

    def _rebuild_sort_mapping(self):
        self._sort_mapping = list(range(len(self._data)))
        if self._sort_column > 0:
            self._apply_sort()

    def _apply_sort(self):
        data_col = self._sort_column - 1
        if data_col < 0 or data_col >= len(self._columns):
            return

        key = self._columns[data_col]['key']
        reverse = self._sort_order == Qt.DescendingOrder

        sample = None
        for d in self._data:
            v = d.get(key)
            if v is not None:
                sample = v
                break

        is_numeric = isinstance(sample, (int, float)) and not isinstance(sample, bool)

        def sort_key(data_idx):
            val = self._data[data_idx].get(key) if data_idx < len(self._data) else None
            if val is None:
                return None
            if is_numeric:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return str(val)
            return str(val)

        non_none = [i for i in self._sort_mapping if sort_key(i) is not None]
        none_vals = [i for i in self._sort_mapping if sort_key(i) is None]

        non_none.sort(key=sort_key, reverse=reverse)
        self._sort_mapping = non_none + none_vals

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._sort_mapping)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else (1 + len(self._columns))

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        if row < 0 or row >= len(self._sort_mapping):
            return None

        data_idx = self._sort_mapping[row]

        if col == 0:
            if role == Qt.CheckStateRole:
                return Qt.Checked if data_idx in self._checked_rows else Qt.Unchecked
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None

        data_col = col - 1
        if data_col < 0 or data_col >= len(self._columns):
            return None

        key = self._columns[data_col]['key']
        value = self._data[data_idx].get(key) if data_idx < len(self._data) else None

        if role == Qt.DisplayRole:
            return '' if value is None else str(value)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        if role == Qt.UserRole:
            return value

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        row, col = index.row(), index.column()
        if row < 0 or row >= len(self._sort_mapping):
            return False

        data_idx = self._sort_mapping[row]

        if col == 0 and role == Qt.CheckStateRole:
            if value == Qt.Checked:
                self._checked_rows.add(data_idx)
            else:
                self._checked_rows.discard(data_idx)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        col = index.column()
        flags = Qt.ItemIsEnabled

        if col == 0:
            flags |= Qt.ItemIsUserCheckable
        else:
            flags |= Qt.ItemIsSelectable

        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return ''
                data_col = section - 1
                if 0 <= data_col < len(self._columns):
                    return self._columns[data_col].get('label', '')
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter if section == 0 else (Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        if column == 0:
            return

        old_persistent = self.persistentIndexList()
        old_mapping = list(self._sort_mapping)

        self.layoutAboutToBeChanged.emit()

        self._sort_column = column
        self._sort_order = order
        self._apply_sort()

        new_indexes = []
        for idx in old_persistent:
            data_row = old_mapping[idx.row()] if idx.row() < len(old_mapping) else -1
            if data_row >= 0:
                try:
                    new_row = self._sort_mapping.index(data_row)
                except ValueError:
                    new_row = idx.row()
            else:
                new_row = idx.row()
            new_indexes.append(self.index(new_row, idx.column()))

        self.changePersistentIndexList(old_persistent, new_indexes)
        self.layoutChanged.emit()

    def get_row_data(self, visual_row):
        if 0 <= visual_row < len(self._sort_mapping):
            data_idx = self._sort_mapping[visual_row]
            if data_idx < len(self._data):
                return dict(self._data[data_idx])
        return None

    def get_checked_data(self):
        return [dict(self._data[i]) for i in sorted(self._checked_rows) if i < len(self._data)]

    def get_checked_count(self):
        return len(self._checked_rows)

    def get_total_count(self):
        return self._total_count

    def get_loaded_count(self):
        return len(self._data)

    def can_load_more(self):
        return len(self._data) < self._total_count

    def set_total_count(self, count):
        self._total_count = count

    def clear_checked(self):
        if not self._checked_rows:
            return
        self._checked_rows.clear()
        if self._sort_mapping:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self._sort_mapping) - 1, 0),
                [Qt.CheckStateRole]
            )


# ═══════════════════════════════════════════════════════════════════════
#  CHECKBOX DELEGATE
# ═══════════════════════════════════════════════════════════════════════

class CheckboxDelegate(QStyledItemDelegate):
    """Paints a centered checkbox in column 0 without interfering with row highlight."""

    def paint(self, painter, option, index):
        painter.save()

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        check_state = index.data(Qt.CheckStateRole)
        check_option = QStyleOptionButton()
        check_option.state = QStyle.State_Enabled
        check_option.state |= QStyle.State_On if check_state == Qt.Checked else QStyle.State_Off

        indicator_rect = QApplication.style().subElementRect(
            QStyle.SE_CheckBoxIndicator, check_option, None
        )
        x = option.rect.x() + (option.rect.width() - indicator_rect.width()) // 2
        y = option.rect.y() + (option.rect.height() - indicator_rect.height()) // 2
        check_option.rect = QRect(x, y, indicator_rect.width(), indicator_rect.height())

        QApplication.style().drawControl(QStyle.CE_CheckBox, check_option, painter)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        return False  # Handled directly in ErpTableView

    def sizeHint(self, option, index):
        return QSize(40, 30)


# ═══════════════════════════════════════════════════════════════════════
#  TABLE VIEW
# ═══════════════════════════════════════════════════════════════════════

class ErpTableView(QTableView):
    rowDoubleClicked = pyqtSignal(dict)
    contextMenuRequested = pyqtSignal(int)
    loadMoreRequested = pyqtSignal()

    CHECKBOX_COL_WIDTH = 40
    SCROLL_THRESHOLD = 5

    def __init__(self, row_height=32, parent=None):
        super().__init__(parent)
        self._row_height = row_height
        self._context_actions = []
        self._is_loading = False
        self._empty_text = "No data found"
        self._configure()

    def _configure(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setMinimumSectionSize(50)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setModel(self, model):
        super().setModel(model)
        self._apply_column_config()
        self.setItemDelegateForColumn(0, CheckboxDelegate(self))
        self.verticalHeader().setDefaultSectionSize(self._row_height)

    def _apply_column_config(self):
        model = self.model()
        if not model:
            return
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, self.CHECKBOX_COL_WIDTH)
        for col in range(1, model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            self.setColumnWidth(col, 150)
        header.setStretchLastSection(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid() and index.column() == 0:
                model = self.model()
                state = index.data(Qt.CheckStateRole)
                new_state = Qt.Unchecked if state == Qt.Checked else Qt.Checked
                model.setData(index, new_state, Qt.CheckStateRole)
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() > 0:
            model = self.model()
            if hasattr(model, 'get_row_data'):
                data = model.get_row_data(index.row())
                if data:
                    self.rowDoubleClicked.emit(data)
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            indexes = self.selectedIndexes()
            if indexes:
                model = self.model()
                if hasattr(model, 'get_row_data'):
                    data = model.get_row_data(indexes[0].row())
                    if data:
                        self.rowDoubleClicked.emit(data)
            return
        if key == Qt.Key_Delete:
            return
        if key == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            return
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        if not self._context_actions:
            return

        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        self.selectRow(index.row())
        self.contextMenuRequested.emit(index.row())

        menu = QMenu(self)
        for action in self._context_actions:
            menu.addAction(action)
        menu.exec_(event.globalPos())

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self._check_scroll_for_load_more()

    def _check_scroll_for_load_more(self):
        if self._is_loading:
            return
        model = self.model()
        if not model or not hasattr(model, 'can_load_more'):
            return
        if not model.can_load_more():
            return
        scrollbar = self.verticalScrollBar()
        if scrollbar.maximum() - scrollbar.value() <= self.SCROLL_THRESHOLD:
            self.loadMoreRequested.emit()

    def paintEvent(self, event):
        super().paintEvent(event)
        model = self.model()
        if model and model.rowCount() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(160, 160, 160))
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, self._empty_text)
            painter.end()

    def set_context_actions(self, actions):
        self._context_actions = list(actions) if actions else []

    def set_loading(self, loading):
        self._is_loading = loading

    def set_empty_text(self, text):
        self._empty_text = text


# ═══════════════════════════════════════════════════════════════════════
#  LOADING OVERLAY
# ═══════════════════════════════════════════════════════════════════════

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._active = False

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.hide()

    def show_overlay(self):
        self._active = True
        self._angle = 0
        self._timer.start(40)
        self.show()
        self.raise_()

    def hide_overlay(self):
        self._active = False
        self._timer.stop()
        self.hide()

    def _rotate(self):
        self._angle = (self._angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        if not self._active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 180))

        center = self.rect().center()
        radius = 22

        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)

        for i in range(12):
            angle = (self._angle + i * 30) % 360
            alpha = int(255 * (1 - i / 12))
            pen.setColor(QColor(80, 80, 80, alpha))
            painter.setPen(pen)

            rad = math.radians(angle)
            x1 = center.x() + int((radius - 8) * math.cos(rad))
            y1 = center.y() + int((radius - 8) * math.sin(rad))
            x2 = center.x() + int(radius * math.cos(rad))
            y2 = center.y() + int(radius * math.sin(rad))
            painter.drawLine(x1, y1, x2, y2)

        painter.setPen(QColor(100, 100, 100))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(
            QRect(center.x() - 60, center.y() + 30, 120, 24),
            Qt.AlignCenter, "Loading..."
        )
        painter.end()

    def mousePressEvent(self, event):
        if self._active: event.accept(); return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._active: event.accept(); return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._active: event.accept(); return
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if self._active: event.accept(); return
        super().wheelEvent(event)


# ═══════════════════════════════════════════════════════════════════════
#  FOOTER / STATUS SECTION
# ═══════════════════════════════════════════════════════════════════════

class FooterWidget(QFrame):
    refreshRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self._total_label = QLabel("Total: 0")
        self._selected_label = QLabel("Selected: 0")
        self._loaded_label = QLabel("Loaded: 0 / 0")

        left = QWidget()
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.addWidget(self._total_label)
        left_layout.addWidget(self._separator())
        left_layout.addWidget(self._selected_label)
        left_layout.addWidget(self._separator())
        left_layout.addWidget(self._loaded_label)
        left_layout.addStretch()

        self._refresh_btn = QPushButton("↻ Refresh")
        self._refresh_btn.setFixedSize(95, 26)
        self._refresh_btn.setFocusPolicy(Qt.NoFocus)
        self._refresh_btn.clicked.connect(self.refreshRequested.emit)

        layout.addWidget(left, 1)
        layout.addWidget(self._refresh_btn)

    @staticmethod
    def _separator():
        sep = QLabel("|")
        sep.setStyleSheet("color: #bbb;")
        return sep

    def update_counts(self, total, selected, loaded, total_available):
        self._total_label.setText(f"Total: {total}")
        self._selected_label.setText(f"Selected: {selected}")
        self._loaded_label.setText(f"Loaded: {loaded} / {total_available}")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN COMPOSITE WIDGET
# ═══════════════════════════════════════════════════════════════════════

class ErpTableWidget(QWidget):
    rowDoubleClicked = pyqtSignal(dict)
    selectionChanged = pyqtSignal(list)
    refreshRequested = pyqtSignal()
    contextMenuRequested = pyqtSignal(int)
    loadMoreRequested = pyqtSignal()

    def __init__(self, columns_config=None, chunk_size=50, row_height=32, parent=None):
        super().__init__(parent)
        self._columns_config = columns_config or []
        self._chunk_size = chunk_size
        self._row_height = row_height
        self._is_loading = False

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._table_view = ErpTableView(row_height=self._row_height)
        self._model = ErpTableModel(self._columns_config)
        self._table_view.setModel(self._model)

        self._loading_overlay = LoadingOverlay(self._table_view.viewport())
        self._table_view.viewport().installEventFilter(self)

        self._footer = FooterWidget()

        layout.addWidget(self._table_view, 1)
        layout.addWidget(self._footer)

    def _setup_connections(self):
        tv = self._table_view

        tv.rowDoubleClicked.connect(self.rowDoubleClicked.emit)
        tv.contextMenuRequested.connect(self.contextMenuRequested.emit)
        tv.loadMoreRequested.connect(self._on_load_more_requested)

        self._footer.refreshRequested.connect(self.refreshRequested.emit)

        self._model.dataChanged.connect(self._on_model_data_changed)

        sel_model = tv.selectionModel()
        if sel_model:
            sel_model.selectionChanged.connect(self._on_highlight_changed)

    def eventFilter(self, obj, event):
        if obj is self._table_view.viewport() and event.type() == QEvent.Resize:
            self._loading_overlay.setGeometry(self._table_view.viewport().rect())
        return super().eventFilter(obj, event)

    def _on_load_more_requested(self):
        if not self._is_loading:
            self.loadMoreRequested.emit()

    def _on_model_data_changed(self, topLeft, bottomRight, roles):
        if not roles or Qt.CheckStateRole in roles:
            self._update_footer()
            self.selectionChanged.emit(self._model.get_checked_data())

    def _on_highlight_changed(self, selected, deselected):
        pass  # Independent from checkbox selection

    def _update_footer(self):
        loaded = self._model.get_loaded_count()
        total = self._model.get_total_count()
        self._footer.update_counts(
            total=total,
            selected=self._model.get_checked_count(),
            loaded=loaded,
            total_available=total
        )

    # ── Public API ───────────────────────────────────────────────────

    def set_columns(self, columns_config):
        self._columns_config = columns_config
        self._model.set_columns(columns_config)
        self._table_view._apply_column_config()

    def load_data(self, data, total_count=0, is_refresh=True):
        if is_refresh:
            self._model.clear_checked()
        self._model.set_data(data, total_count)
        self._update_footer()

    def append_data(self, data, total_count=0):
        self._model.append_data(data)
        if total_count > 0:
            self._model.set_total_count(total_count)
        self._update_footer()

    def set_loading(self, state):
        self._is_loading = state
        self._table_view.set_loading(state)
        if state:
            self._loading_overlay.show_overlay()
            self._table_view.setEnabled(False)
            self._footer.setEnabled(False)
        else:
            self._loading_overlay.hide_overlay()
            self._table_view.setEnabled(True)
            self._footer.setEnabled(True)

    def set_context_actions(self, actions):
        self._table_view.set_context_actions(actions)

    def clear_selection(self):
        self._model.clear_checked()

    def get_selected_rows(self):
        return self._model.get_checked_data()

    def refresh_view(self):
        self._update_footer()


# ═══════════════════════════════════════════════════════════════════════
#  TEST APPLICATION
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply a clean, generic global stylesheet
    app.setStyleSheet("""
        QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
        QTableView { border: 1px solid #ddd; background-color: #fff; alternate-background-color: #f9f9f9; }
        QHeaderView::section { background-color: #f0f0f0; padding: 6px; border: none; border-bottom: 2px solid #ddd; font-weight: bold; }
        QTableView::item:selected { background-color: #e0f0ff; color: #000; }
        QPushButton { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; padding: 4px 12px; }
        QPushButton:hover { background-color: #e0e0e0; }
        QFrame { background-color: #fafafa; border-top: 1px solid #ddd; }
        QLabel { color: #555; }
    """)

    # Mock Data Configuration
    COLUMNS = [
        {"key": "id", "label": "ID"},
        {"key": "name", "label": "Full Name"},
        {"key": "email", "label": "Email Address"},
        {"key": "role", "label": "Role"},
        {"key": "status", "label": "Status"}
    ]
    
    TOTAL_ROWS = 500
    CHUNK_SIZE = 50
    current_loaded = 0

    # Helper to generate mock rows
    def generate_chunk(start_id, count):
        roles = ["Admin", "Manager", "User", "Guest"]
        statuses = ["Active", "Inactive", "Pending"]
        chunk = []
        for i in range(count):
            uid = start_id + i
            chunk.append({
                "id": uid,
                "name": f"User {uid}",
                "email": f"user{uid}@erp.com",
                "role": random.choice(roles),
                "status": random.choice(statuses)
            })
        return chunk

    # Main Window Setup
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.setContentsMargins(10, 10, 10, 10)

    table = ErpTableWidget(columns_config=COLUMNS, chunk_size=CHUNK_SIZE, row_height=36)
    layout.addWidget(table)

    # Inject Context Menu Actions dynamically
    edit_action = QAction("Edit User", table)
    delete_action = QAction("Delete User", table)
    table.set_context_actions([edit_action, delete_action])

    # Info label for test events
    info_label = QLabel("Events will appear here...")
    info_label.setWordWrap(True)
    layout.addWidget(info_label)

    # Signals Connections
    def on_double_click(data):
        info_label.setText(f"Double-Clicked / Enter: {data['name']} (ID: {data['id']})")

    def on_selection_changed(rows):
        ids = [str(r['id']) for r in rows]
        info_label.setText(f"Checkbox Selection Changed. Selected IDs: {', '.join(ids) if ids else 'None'}")

    def on_context_menu(row):
        data = table._model.get_row_data(row)
        if data:
            info_label.setText(f"Context Menu Requested for: {data['name']}")

    def on_refresh():
        global current_loaded
        info_label.setText("Refresh Requested... Reloading all data.")
        table.set_loading(True)
        QTimer.singleShot(1500, lambda: start_loading(refresh=True))  # Simulate network delay

    def on_load_more():
        global current_loaded
        if current_loaded >= TOTAL_ROWS:
            return
        info_label.setText(f"Lazy Load Requested... Loading next chunk.")
        table.set_loading(True)
        QTimer.singleShot(800, load_next_chunk)  # Simulate network delay

    table.rowDoubleClicked.connect(on_double_click)
    table.selectionChanged.connect(on_selection_changed)
    table.contextMenuRequested.connect(on_context_menu)
    table.refreshRequested.connect(on_refresh)
    table.loadMoreRequested.connect(on_load_more)

    # Loading Simulation Logic
    def start_loading(refresh=False):
        global current_loaded
        if refresh:
            current_loaded = 0
        
        chunk = generate_chunk(current_loaded + 1, CHUNK_SIZE)
        current_loaded += len(chunk)
        
        if refresh:
            table.load_data(chunk, total_count=TOTAL_ROWS, is_refresh=True)
        else:
            table.append_data(chunk, total_count=TOTAL_ROWS)
            
        table.set_loading(False)

    def load_next_chunk():
        start_loading(refresh=False)

    # Initial Load
    start_loading(refresh=True)

    window.resize(900, 600)
    window.setWindowTitle("ERP Table Widget Test - Lazy Loading & Checkboxes")
    window.show()

    sys.exit(app.exec_())
