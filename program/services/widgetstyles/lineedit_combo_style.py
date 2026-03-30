from typing import Callable, Iterable, List, Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QCompleter, QLineEdit

from program.themes.shared_input_popup_style import apply_lineedit_style, apply_popup_list_style


def apply_lineedit_combo_style(line_edit: QLineEdit) -> None:
    """Apply a light input style used by the app."""
    apply_lineedit_style(line_edit)


class LineEditAutoComplete(QtCore.QObject):
    """Simple line edit autocomplete that filters while typing."""

    def __init__(self, line_edit: QLineEdit, parent=None, **_kwargs):
        super().__init__(parent)
        self.line_edit = line_edit
        self._enabled = True
        self._min_chars_to_show = 0
        self._debounce_ms = 0
        self._force_show_on_focus = False

        self._model = QStringListModel(self.line_edit)
        self._completer = QCompleter(self._model, self.line_edit)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setFilterMode(QtCore.Qt.MatchContains)
        self._completer.activated.connect(self._on_item_activated)
        apply_popup_list_style(self._completer.popup(), row_height=36)
        self.line_edit.setCompleter(self._completer)

        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._refresh_popup)

        self.line_edit.textEdited.connect(self._on_text_edited)
        self.line_edit.destroyed.connect(lambda *_: self._shutdown())
        self.line_edit.installEventFilter(self)

        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._shutdown)

        apply_lineedit_combo_style(self.line_edit)

    def set_items(self, items: Iterable[str]) -> None:
        self._model.setStringList(self._normalize(items))
        if self._is_popup_visible():
            self._schedule_refresh(force=True)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.line_edit.setReadOnly(not self._enabled)
        if not self._enabled:
            self.close_popup()

    def set_min_chars_to_show(self, n: int) -> None:
        self._min_chars_to_show = max(0, int(n))

    def set_debounce_ms(self, ms: int) -> None:
        self._debounce_ms = max(0, int(ms))

    def set_force_show_on_focus(self, enabled: bool) -> None:
        self._force_show_on_focus = bool(enabled)

    def refresh_from(self, fetch_items_fn: Callable[[], Iterable[str]]) -> None:
        self.set_items(fetch_items_fn())

    def open_popup(self) -> None:
        self._schedule_refresh(force=True)

    def close_popup(self) -> None:
        try:
            self._completer.popup().hide()
        except RuntimeError:
            pass

    def eventFilter(self, obj, event):
        if obj is self.line_edit and self._enabled:
            if event.type() == QtCore.QEvent.FocusIn and self._force_show_on_focus:
                QtCore.QTimer.singleShot(0, self.open_popup)
        return super().eventFilter(obj, event)

    def _on_text_edited(self, _text: str) -> None:
        self._schedule_refresh()

    def _on_item_activated(self, text: str) -> None:
        self._refresh_timer.stop()
        self.line_edit.setText(text)
        self.close_popup()

    def _schedule_refresh(self, force: bool = False) -> None:
        if not self._enabled or not self.line_edit.isEnabled() or self.line_edit.isReadOnly():
            return

        text = self.line_edit.text().strip()
        if not force and len(text) < self._min_chars_to_show:
            self.close_popup()
            return

        if self._debounce_ms <= 0 or force:
            self._refresh_timer.stop()
            self._refresh_popup()
            return

        self._refresh_timer.start(self._debounce_ms)

    def _refresh_popup(self) -> None:
        query = self.line_edit.text().strip()
        self._completer.setCompletionPrefix(query)
        if self._completer.completionCount() <= 0:
            self.close_popup()
            return
        apply_popup_list_style(self._completer.popup(), row_height=36)
        self._completer.complete(self.line_edit.rect())

    def _is_popup_visible(self) -> bool:
        try:
            return self._completer.popup().isVisible()
        except RuntimeError:
            return False

    def _shutdown(self) -> None:
        self._refresh_timer.stop()
        self.close_popup()

    @staticmethod
    def _normalize(items: Iterable[Optional[str]]) -> List[str]:
        unique: List[str] = []
        seen = set()
        for raw in items:
            if raw is None:
                continue
            value = str(raw).strip()
            if not value:
                continue
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            unique.append(value)
        unique.sort(key=str.casefold)
        return unique


def replace_combobox_with_lineedit(combo: QtWidgets.QComboBox) -> QLineEdit:
    parent = combo.parentWidget()
    line_edit = QLineEdit(parent)

    line_edit.setObjectName(combo.objectName().replace("combobox", "lineedit"))
    line_edit.setGeometry(combo.geometry())
    line_edit.setMinimumSize(combo.minimumSize())
    line_edit.setMaximumSize(combo.maximumSize())
    line_edit.setSizePolicy(combo.sizePolicy())
    line_edit.setFont(combo.font())
    line_edit.setEnabled(combo.isEnabled())
    line_edit.show()
    line_edit.raise_()

    combo.hide()
    combo.deleteLater()
    return line_edit