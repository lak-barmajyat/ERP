import sys
from typing import Callable, Iterable, List, Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QCompleter, QStyledItemDelegate, QLineEdit, QAbstractScrollArea

def apply_lineedit_combo_style(line_edit: QLineEdit) -> None:
    line_edit.setClearButtonEnabled(True)
    line_edit.setStyleSheet("""
        QLineEdit {
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 8px 12px;
            background: #ffffff;
            color: #000000;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 1px solid #2d7ff9;
        }
    """)


class LineEditAutoComplete(QtCore.QObject):
    def __init__(self, line_edit: QLineEdit, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit

        self._model = QStringListModel(self.line_edit)
        self._completer = QCompleter(self._model, self.line_edit)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setFilterMode(QtCore.Qt.MatchContains)

        ROW_HEIGHT = 36

        class _PopupDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(ROW_HEIGHT)
                return size

        popup = self._completer.popup()
        popup.setUniformItemSizes(True)
        popup.setMouseTracking(True)
        popup.setFocusPolicy(QtCore.Qt.NoFocus)
        popup.setSpacing(0)
        popup.setItemDelegate(_PopupDelegate(popup))
        popup.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        popup.setStyleSheet(
            """
            QListView {
                background: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 2px;
                font-size: 13px;
                color: #111827;
                outline: 0;
            }

            QListView::item {
                margin: 2px;
                padding: 6px 10px;
                border-radius: 8px;
            }

            QListView::item:hover {
                background: #eff6ff;
                color: #1d4ed8;
            }

            QListView::item:selected {
                background: #1d7fd8;
                color: #ffffff;
            }

            QListView::item:!selected {
                background: transparent;
            }

            QListView::indicator {
                width: 0px;
                height: 0px;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px 2px 4px 0px;
            }

            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """
        )

        self.line_edit.setCompleter(self._completer)
        self._completer.activated.connect(self._on_item_chosen)

        self.line_edit.installEventFilter(self)

        apply_lineedit_combo_style(self.line_edit)

    def set_items(self, items: Iterable[str]) -> None:
        cleaned = self._normalize(list(items))
        self._model.setStringList(cleaned)

    def refresh_from(self, fetch_items_fn: Callable[[], Iterable[str]]) -> None:
        self.set_items(fetch_items_fn())

    def eventFilter(self, obj, event):
        if obj is self.line_edit and event.type() == QtCore.QEvent.MouseButtonPress:
            QtCore.QTimer.singleShot(0, self.open_popup)
        return super().eventFilter(obj, event)

    def open_popup(self) -> None:
        if self.line_edit is None:
            return
        self._completer.setCompletionPrefix("")
        self._completer.complete()

    def _on_item_chosen(self, text: str) -> None:
        self.line_edit.setText(text)
        QtCore.QTimer.singleShot(0, lambda: self.line_edit.setFocus(QtCore.Qt.OtherFocusReason))

    @staticmethod
    def _normalize(items: List[Optional[str]]) -> List[str]:
        unique: List[str] = []
        seen = set()
        for raw in items:
            if raw is None:
                continue
            v = str(raw).strip()
            if not v:
                continue
            k = v.casefold()
            if k in seen:
                continue
            seen.add(k)
            unique.append(v)
        unique.sort(key=str.casefold)
        return unique


def replace_combobox_with_lineedit(combo: QtWidgets.QComboBox) -> QLineEdit:
    parent = combo.parentWidget()
    le = QLineEdit(parent)

    le.setObjectName(combo.objectName().replace("combobox", "lineedit"))
    le.setGeometry(combo.geometry())
    le.setMinimumSize(combo.minimumSize())
    le.setMaximumSize(combo.maximumSize())
    le.setSizePolicy(combo.sizePolicy())
    le.setFont(combo.font())
    le.setEnabled(combo.isEnabled())
    le.setVisible(True)
    le.raise_()

    combo.hide()
    combo.deleteLater()
    return le


def _demo():
    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QWidget()
    w.setWindowTitle("LineEdit Combo Style - Demo")
    layout = QtWidgets.QVBoxLayout(w)

    # 1. Style-only LineEdit
    le_style = QLineEdit()
    le_style.setPlaceholderText("Style only - no autocomplete")
    apply_lineedit_combo_style(le_style)
    layout.addWidget(le_style)

    # 2. LineEdit with autocomplete
    le_auto = QLineEdit()
    le_auto.setPlaceholderText("Client (with autocomplete)")
    ac = LineEditAutoComplete(le_auto, w)
    ac.set_items([
        "Ahmed Lak", "Aboubakr Laktawi", "Fatima Laktawi",
        "Mossab Laktawi", "Elhocine Laktawi",
        "Client Casablanca", "Client Rabat", "Client Agadir",
    ])
    layout.addWidget(le_auto)

    btn = QtWidgets.QPushButton("Open suggestions")
    btn.clicked.connect(ac.open_popup)
    layout.addWidget(btn)

    w.resize(400, 180)
    le_style.setFocus()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    _demo()
