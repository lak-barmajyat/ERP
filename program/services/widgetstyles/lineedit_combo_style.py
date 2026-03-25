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
    """
    Robust QLineEdit autocomplete with:
    - MatchContains filtering that updates as user types (textEdited)
    - Debounced popup refresh to avoid flicker / heavy updates
    - Safe handling for enable/disable, focus, ESC, arrows, mouse, IME composition
    - No style changes (keeps your existing QLineEdit and popup styles)
    """

    def __init__(self, line_edit: QLineEdit, func: callable=None, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit
        self._enabled = True

        # Tunables (kept internal; change via setters below)
        self._min_chars_to_show = 0          # show even when empty, like a combo
        self._debounce_ms = 40               # small debounce for smoother typing
        self._force_show_on_focus = True     # open on focus/click (combo-like)
        self._respect_readonly = True        # do not open if line edit is readOnly
        self._suppress_next_text_signal = False

        self._model = QStringListModel(self.line_edit)
        self._completer = QCompleter(self._model, self.line_edit)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setFilterMode(QtCore.Qt.MatchContains)
        if func:
            func

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

        # Activated fires when user chooses an item (click/enter).
        self._completer.activated.connect(self._on_item_chosen)

        # Update results while typing (this is the main fix for "writing inside the entry")
        self.line_edit.textEdited.connect(self._on_text_edited)
        # Some inputs update via programmatic setText; keep it responsive but safe.
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.editingFinished.connect(self._on_editing_finished)

        # Debounce timer to keep UI smooth
        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._refresh_popup_now)

        self.line_edit.installEventFilter(self)

        apply_lineedit_combo_style(self.line_edit)

    # ----------------------------
    # Public API
    # ----------------------------

    def set_items(self, items: Iterable[str]) -> None:
        cleaned = self._normalize(list(items))
        self._model.setStringList(cleaned)

        # If popup is open, refresh to reflect changes immediately.
        if self._is_popup_visible():
            self._schedule_refresh(force=True)

    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable BOTH the line edit interaction and the completer popup."""
        self._enabled = enabled
        self.line_edit.setReadOnly(not enabled)

        # Close popup if disabling
        if not enabled and self._completer:
            popup = self._completer.popup()
            if popup:
                popup.hide()

    def set_min_chars_to_show(self, n: int) -> None:
        """Minimum characters required before suggestions show (0 = show even when empty)."""
        self._min_chars_to_show = max(0, int(n))
        if self._is_popup_visible():
            self._schedule_refresh(force=True)

    def set_debounce_ms(self, ms: int) -> None:
        self._debounce_ms = max(0, int(ms))

    def set_force_show_on_focus(self, enabled: bool) -> None:
        self._force_show_on_focus = bool(enabled)

    def refresh_from(self, fetch_items_fn: Callable[[], Iterable[str]]) -> None:
        self.set_items(fetch_items_fn())

    def open_popup(self) -> None:
        """Force open suggestions using the current input (or empty)."""
        if not self._can_interact():
            return
        self._schedule_refresh(force=True)

    def close_popup(self) -> None:
        if self._completer and self._completer.popup():
            self._completer.popup().hide()

    # ----------------------------
    # Events & internals
    # ----------------------------

    def eventFilter(self, obj, event):
        if obj is self.line_edit:
            if not self._can_interact():
                return False

            et = event.type()

            # Combo-like behavior: open on focus/click (but without overriding typing updates)
            if et in (QtCore.QEvent.FocusIn, QtCore.QEvent.MouseButtonPress):
                if self._force_show_on_focus:
                    QtCore.QTimer.singleShot(0, self.open_popup)

            # Keyboard behavior improvements:
            # - Down arrow opens popup (like combobox)
            # - Esc closes popup
            # - If popup is open, let completer handle navigation keys normally
            if et == QtCore.QEvent.KeyPress:
                key = event.key()
                if key == QtCore.Qt.Key_Escape:
                    if self._is_popup_visible():
                        self.close_popup()
                        return True
                if key in (QtCore.Qt.Key_Down, QtCore.Qt.Key_Up):
                    # If user presses arrows and popup isn't visible, open it.
                    if not self._is_popup_visible():
                        QtCore.QTimer.singleShot(0, self.open_popup)
                        return True

            # If the line edit is resized/moved while popup visible, re-complete to reposition.
            if et in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
                if self._is_popup_visible():
                    self._schedule_refresh(force=True)

        return super().eventFilter(obj, event)

    def _on_text_edited(self, _text: str) -> None:
        # textEdited is only user edits (good signal to update popup)
        if self._suppress_next_text_signal:
            return
        self._schedule_refresh()

    def _on_text_changed(self, _text: str) -> None:
        # This catches programmatic changes too; update only if popup visible or focus is on edit.
        if self._suppress_next_text_signal:
            return
        if self._is_popup_visible() or self.line_edit.hasFocus():
            self._schedule_refresh()

    def _on_editing_finished(self) -> None:
        # Close popup on editing finished to reduce visual leftovers.
        self.close_popup()

    def _schedule_refresh(self, force: bool = False) -> None:
        if not self._can_interact():
            return

        # Don't show if not enough chars unless forced.
        if not force:
            if len(self.line_edit.text().strip()) < self._min_chars_to_show:
                # Hide any existing popup (since user erased text, etc.)
                if self._is_popup_visible():
                    self.close_popup()
                return

        # Debounce
        if self._debounce_ms <= 0 or force:
            self._refresh_timer.stop()
            self._refresh_popup_now()
            return

        self._refresh_timer.start(self._debounce_ms)

    def _refresh_popup_now(self) -> None:
        if not self._can_interact():
            return
        if not self._completer:
            return

        prefix = self.line_edit.text()
        # For MatchContains, completionPrefix is still the query input for filtering.
        self._completer.setCompletionPrefix(prefix)

        # If there are no matches, hide popup to avoid "empty" list.
        if self._completer.completionCount() <= 0:
            self.close_popup()
            return

        # Ensure the popup is aligned to the line edit and sized nicely.
        rect = self.line_edit.rect()
        rect.setWidth(max(rect.width(), self._suggested_popup_width()))
        self._completer.complete(rect)

    def _suggested_popup_width(self) -> int:
        # Keep it at least the line edit width; allow popup to grow a bit if needed.
        # We don't force a maximum here to keep it flexible.
        try:
            return self.line_edit.width()
        except Exception:
            return 0

    def _is_popup_visible(self) -> bool:
        try:
            popup = self._completer.popup() if self._completer else None
            return bool(popup and popup.isVisible())
        except Exception:
            return False

    def _can_interact(self) -> bool:
        if not self._enabled:
            return False
        if not self.line_edit or not self.line_edit.isEnabled():
            return False
        if self._respect_readonly and self.line_edit.isReadOnly():
            return False
        return True

    def _on_item_chosen(self, text: str) -> None:
        # Avoid re-entrant refresh loops while setting the chosen text.
        self._suppress_next_text_signal = True
        try:
            self.line_edit.setText(text)
        finally:
            self._suppress_next_text_signal = False

        # Keep focus on the line edit after choosing.
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

    # Optional tuning examples (keep defaults if you want combo-like behavior)
    # ac.set_min_chars_to_show(1)
    # ac.set_debounce_ms(30)

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