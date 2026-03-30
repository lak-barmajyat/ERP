import json
import os
import re

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLineEdit, QStyledItemDelegate


def _load_tokens():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tokens_path = os.path.join(base_dir, "widget_style_tokens.json")
    with open(tokens_path, "r", encoding="utf-8") as f:
        return json.load(f)


T = _load_tokens()

FONT_FAMILY = T["FONT_FAMILY"]
FONT_WEIGHT = int(T["FONT_WEIGHT"])
FONT_SIZE_PT = int(T["FONT_SIZE_PT"])
MENU_FONT_WEIGHT = int(T["MENU_FONT_WEIGHT"])
MENU_FONT_SIZE_PT = int(T["MENU_FONT_SIZE_PT"])

BORDER_SIZE = int(T["BORDER_SIZE"])
RADIUS_INPUT = int(T["RADIUS_INPUT"])
RADIUS_POPUP = int(T["RADIUS_POPUP"])
RADIUS_ITEM = int(T["RADIUS_ITEM"])
RADIUS_SCROLLBAR = int(T["RADIUS_SCROLLBAR"])

INPUT_PADDING_Y = int(T["INPUT_PADDING_Y"])
INPUT_PADDING_X = int(T["INPUT_PADDING_X"])
COMBO_PADDING_RIGHT = int(T["COMBO_PADDING_RIGHT"])
POPUP_PADDING = int(T["POPUP_PADDING"])
ITEM_MARGIN = int(T["ITEM_MARGIN"])
ITEM_PADDING_Y = int(T["ITEM_PADDING_Y"])
ITEM_PADDING_X = int(T["ITEM_PADDING_X"])
MENU_PADDING = int(T["MENU_PADDING"])
MENU_ITEM_PADDING_Y = int(T["MENU_ITEM_PADDING_Y"])
MENU_ITEM_PADDING_X = int(T["MENU_ITEM_PADDING_X"])
MENU_SEPARATOR_MARGIN_Y = int(T["MENU_SEPARATOR_MARGIN_Y"])
MENU_SEPARATOR_MARGIN_X = int(T["MENU_SEPARATOR_MARGIN_X"])

SCROLLBAR_WIDTH = int(T["SCROLLBAR_WIDTH"])
SCROLLBAR_HANDLE_MIN_HEIGHT = int(T["SCROLLBAR_HANDLE_MIN_HEIGHT"])
DROPDOWN_WIDTH = int(T["DROPDOWN_WIDTH"])
ARROW_SIZE = int(T["ARROW_SIZE"])
MENU_MIN_WIDTH = int(T["MENU_MIN_WIDTH"])
MENU_ITEM_MIN_WIDTH = int(T["MENU_ITEM_MIN_WIDTH"])

COLOR_BG = T["COLOR_BG"]
COLOR_BG_SOFT = T["COLOR_BG_SOFT"]
COLOR_TEXT = T["COLOR_TEXT"]
COLOR_TEXT_POPUP = T["COLOR_TEXT_POPUP"]
COLOR_TEXT_MUTED = T["COLOR_TEXT_MUTED"]
COLOR_TEXT_DISABLED = T["COLOR_TEXT_DISABLED"]
COLOR_PLACEHOLDER = T["COLOR_PLACEHOLDER"]

COLOR_BORDER = T["COLOR_BORDER"]
COLOR_BORDER_HOVER = T["COLOR_BORDER_HOVER"]
COLOR_FOCUS = T["COLOR_FOCUS"]

COLOR_ITEM_HOVER_BG = T["COLOR_ITEM_HOVER_BG"]
COLOR_ITEM_HOVER_TEXT = T["COLOR_ITEM_HOVER_TEXT"]
COLOR_ITEM_HOVER_BORDER = T["COLOR_ITEM_HOVER_BORDER"]
COLOR_ITEM_SELECTED_BG = T["COLOR_ITEM_SELECTED_BG"]
COLOR_ITEM_SELECTED_TEXT = T["COLOR_ITEM_SELECTED_TEXT"]
COLOR_ITEM_SELECTED_BORDER = T["COLOR_ITEM_SELECTED_BORDER"]

COLOR_MENU_ITEM_HOVER_BG = T["COLOR_MENU_ITEM_HOVER_BG"]
COLOR_MENU_ITEM_HOVER_TEXT = T["COLOR_MENU_ITEM_HOVER_TEXT"]

COLOR_DISABLED_BG = T["COLOR_DISABLED_BG"]

COLOR_SCROLLBAR_HANDLE = T["COLOR_SCROLLBAR_HANDLE"]
COLOR_SCROLLBAR_HANDLE_HOVER = T["COLOR_SCROLLBAR_HANDLE_HOVER"]

BUTTON_PRIMARY_BG = T["BUTTON_PRIMARY_BG"]
BUTTON_PRIMARY_BG_HOVER = T["BUTTON_PRIMARY_BG_HOVER"]
BUTTON_PRIMARY_BG_PRESSED = T["BUTTON_PRIMARY_BG_PRESSED"]
BUTTON_PRIMARY_TEXT = T["BUTTON_PRIMARY_TEXT"]
BUTTON_PRIMARY_BORDER = T["BUTTON_PRIMARY_BORDER"]
BUTTON_PRIMARY_BORDER_HOVER = T["BUTTON_PRIMARY_BORDER_HOVER"]
BUTTON_PRIMARY_BORDER_PRESSED = T["BUTTON_PRIMARY_BORDER_PRESSED"]
BUTTON_PRIMARY_RADIUS = int(T["BUTTON_PRIMARY_RADIUS"])
BUTTON_PRIMARY_HEIGHT = int(T["BUTTON_PRIMARY_HEIGHT"])
BUTTON_PRIMARY_PADDING_Y = int(T["BUTTON_PRIMARY_PADDING_Y"])
BUTTON_PRIMARY_PADDING_X = int(T["BUTTON_PRIMARY_PADDING_X"])
BUTTON_PRIMARY_FONT_WEIGHT = int(T["BUTTON_PRIMARY_FONT_WEIGHT"])
BUTTON_PRIMARY_FONT_SIZE_PT = int(T["BUTTON_PRIMARY_FONT_SIZE_PT"])
BUTTON_PRIMARY_TEXT_TRANSFORM = T["BUTTON_PRIMARY_TEXT_TRANSFORM"]
BUTTON_PRIMARY_DISABLED_BG = T["BUTTON_PRIMARY_DISABLED_BG"]
BUTTON_PRIMARY_DISABLED_TEXT = T["BUTTON_PRIMARY_DISABLED_TEXT"]
BUTTON_PRIMARY_DISABLED_BORDER = T["BUTTON_PRIMARY_DISABLED_BORDER"]

BUTTON_TOOLBAR_BG = T["BUTTON_TOOLBAR_BG"]
BUTTON_TOOLBAR_BG_HOVER = T["BUTTON_TOOLBAR_BG_HOVER"]
BUTTON_TOOLBAR_BG_PRESSED = T["BUTTON_TOOLBAR_BG_PRESSED"]
BUTTON_TOOLBAR_TEXT = T["BUTTON_TOOLBAR_TEXT"]
BUTTON_TOOLBAR_BORDER = T["BUTTON_TOOLBAR_BORDER"]
BUTTON_TOOLBAR_RADIUS = int(T["BUTTON_TOOLBAR_RADIUS"])
BUTTON_TOOLBAR_HEIGHT = int(T["BUTTON_TOOLBAR_HEIGHT"])
BUTTON_TOOLBAR_PADDING_Y = int(T["BUTTON_TOOLBAR_PADDING_Y"])
BUTTON_TOOLBAR_PADDING_X = int(T["BUTTON_TOOLBAR_PADDING_X"])
BUTTON_TOOLBAR_FONT_WEIGHT = int(T["BUTTON_TOOLBAR_FONT_WEIGHT"])
BUTTON_TOOLBAR_FONT_SIZE_PT = int(T["BUTTON_TOOLBAR_FONT_SIZE_PT"])
BUTTON_TOOLBAR_TEXT_TRANSFORM = T["BUTTON_TOOLBAR_TEXT_TRANSFORM"]
BUTTON_TOOLBAR_DISABLED_BG = T["BUTTON_TOOLBAR_DISABLED_BG"]
BUTTON_TOOLBAR_DISABLED_TEXT = T["BUTTON_TOOLBAR_DISABLED_TEXT"]
BUTTON_TOOLBAR_DISABLED_BORDER = T["BUTTON_TOOLBAR_DISABLED_BORDER"]

BUTTON_SECONDARY_BG = T["BUTTON_SECONDARY_BG"]
BUTTON_SECONDARY_BG_HOVER = T["BUTTON_SECONDARY_BG_HOVER"]
BUTTON_SECONDARY_BG_PRESSED = T["BUTTON_SECONDARY_BG_PRESSED"]
BUTTON_SECONDARY_TEXT = T["BUTTON_SECONDARY_TEXT"]
BUTTON_SECONDARY_TEXT_HOVER = T["BUTTON_SECONDARY_TEXT_HOVER"]
BUTTON_SECONDARY_BORDER = T["BUTTON_SECONDARY_BORDER"]
BUTTON_SECONDARY_BORDER_HOVER = T["BUTTON_SECONDARY_BORDER_HOVER"]
BUTTON_SECONDARY_BORDER_PRESSED = T["BUTTON_SECONDARY_BORDER_PRESSED"]
BUTTON_SECONDARY_RADIUS = int(T["BUTTON_SECONDARY_RADIUS"])
BUTTON_SECONDARY_HEIGHT = int(T["BUTTON_SECONDARY_HEIGHT"])
BUTTON_SECONDARY_PADDING_Y = int(T["BUTTON_SECONDARY_PADDING_Y"])
BUTTON_SECONDARY_PADDING_X = int(T["BUTTON_SECONDARY_PADDING_X"])
BUTTON_SECONDARY_FONT_WEIGHT = int(T["BUTTON_SECONDARY_FONT_WEIGHT"])
BUTTON_SECONDARY_FONT_SIZE_PT = int(T["BUTTON_SECONDARY_FONT_SIZE_PT"])
BUTTON_SECONDARY_TEXT_TRANSFORM = T["BUTTON_SECONDARY_TEXT_TRANSFORM"]
BUTTON_SECONDARY_DISABLED_BG = T["BUTTON_SECONDARY_DISABLED_BG"]
BUTTON_SECONDARY_DISABLED_TEXT = T["BUTTON_SECONDARY_DISABLED_TEXT"]
BUTTON_SECONDARY_DISABLED_BORDER = T["BUTTON_SECONDARY_DISABLED_BORDER"]


COMPLETER_POPUP_QSS = f"""
QListView {{
    background: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_POPUP}px;
    padding: {POPUP_PADDING}px;
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT_POPUP};
    outline: 0;
}}

QListView::item {{
    margin: {ITEM_MARGIN}px;
    padding: {ITEM_PADDING_Y}px {ITEM_PADDING_X}px;
    border-radius: {RADIUS_ITEM}px;
    border: {BORDER_SIZE}px solid transparent;
}}

QListView::item:hover:!selected {{
    background: {COLOR_ITEM_HOVER_BG};
    color: {COLOR_ITEM_HOVER_TEXT};
    border: {BORDER_SIZE}px solid {COLOR_ITEM_HOVER_BORDER};
}}

QListView::item:selected {{
    background: {COLOR_ITEM_SELECTED_BG};
    color: {COLOR_ITEM_SELECTED_TEXT};
    border: {BORDER_SIZE}px solid {COLOR_ITEM_SELECTED_BORDER};
}}

QListView::item:selected:hover {{
    background: {COLOR_ITEM_SELECTED_BG};
    color: {COLOR_ITEM_SELECTED_TEXT};
    border: {BORDER_SIZE}px solid {COLOR_ITEM_SELECTED_BORDER};
}}

QListView::item:disabled {{
    color: {COLOR_TEXT_DISABLED};
}}

QListView::indicator {{
    width: 0px;
    height: 0px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: {SCROLLBAR_WIDTH}px;
    margin: 4px 2px 4px 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_SCROLLBAR_HANDLE};
    border-radius: {RADIUS_SCROLLBAR}px;
    min-height: {SCROLLBAR_HANDLE_MIN_HEIGHT}px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_SCROLLBAR_HANDLE_HOVER};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""


TABLE_POPUP_QSS = f"""
QTableView {{
    background: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_POPUP}px;
    padding: {POPUP_PADDING}px;
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT_POPUP};
    gridline-color: transparent;
    outline: 0;
}}

QTableView::item {{
    border: {BORDER_SIZE}px solid transparent;
    padding: {ITEM_PADDING_Y}px {ITEM_PADDING_X}px;
}}

QTableView::item:hover:!selected {{
    background: {COLOR_ITEM_HOVER_BG};
    color: {COLOR_ITEM_HOVER_TEXT};
}}

QTableView::item:selected {{
    background: {COLOR_ITEM_SELECTED_BG};
    color: {COLOR_ITEM_SELECTED_TEXT};
}}
"""


ENTRY_QSS = f"""
QLineEdit {{
    background-color: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_INPUT}px;
    padding: {INPUT_PADDING_Y}px {INPUT_PADDING_X}px;
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT};
}}

QLineEdit:hover {{
    border-color: {COLOR_BORDER_HOVER};
}}

QLineEdit:focus {{
    border-color: {COLOR_FOCUS};
}}

QLineEdit:read-only {{
    background-color: {COLOR_BG_SOFT};
    color: {COLOR_TEXT_MUTED};
}}

QLineEdit:disabled {{
    color: {COLOR_TEXT_DISABLED};
    background: {COLOR_DISABLED_BG};
    border-color: {COLOR_BORDER};
}}
"""


COMBOBOX_QSS = f"""
QComboBox {{
    background-color: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_INPUT}px;
    padding: {INPUT_PADDING_Y}px {INPUT_PADDING_X}px;
    padding-right: {COMBO_PADDING_RIGHT}px;
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT};
}}

QComboBox:hover {{
    border-color: {COLOR_BORDER_HOVER};
    background-color: {COLOR_BG};
}}

QComboBox:focus,
QComboBox:on {{
    border-color: {COLOR_FOCUS};
    background-color: {COLOR_BG};
}}

QComboBox::drop-down {{
    border: none;
    width: {DROPDOWN_WIDTH}px;
}}

QComboBox::down-arrow {{
    image: url(program/assets/global/down_blue_arrow.svg);
    width: {ARROW_SIZE}px;
    height: {ARROW_SIZE}px;
}}

QComboBox:disabled {{
    color: {COLOR_TEXT_DISABLED};
    background: {COLOR_DISABLED_BG};
    border-color: {COLOR_BORDER};
}}
"""


DATEEDIT_QSS = f"""
QDateEdit {{
    background-color: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_INPUT}px;
    padding: {INPUT_PADDING_Y}px {INPUT_PADDING_X}px;
    padding-right: {COMBO_PADDING_RIGHT}px;
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT};
}}

QDateEdit:hover {{
    border-color: {COLOR_BORDER_HOVER};
    background-color: {COLOR_BG};
}}

QDateEdit:focus,
QDateEdit:on {{
    border-color: {COLOR_FOCUS};
    background-color: {COLOR_BG};
}}

QDateEdit::drop-down {{
    border: none;
    width: {DROPDOWN_WIDTH}px;
}}

QDateEdit::down-arrow {{
    image: url(program/assets/global/down_blue_arrow.svg);
    width: {ARROW_SIZE}px;
    height: {ARROW_SIZE}px;
}}

QDateEdit:disabled {{
    color: {COLOR_TEXT_DISABLED};
    background: {COLOR_DISABLED_BG};
    border-color: {COLOR_BORDER};
}}
"""


MENU_QSS = f"""
QMenu {{
    background-color: {COLOR_BG};
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-radius: {RADIUS_POPUP}px;
    padding: {MENU_PADDING}px;
    font: {MENU_FONT_WEIGHT} {MENU_FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
    color: {COLOR_TEXT};
}}

QMenu::item {{
    padding: {MENU_ITEM_PADDING_Y}px {MENU_ITEM_PADDING_X}px;
    border-radius: {max(2, RADIUS_ITEM - 2)}px;
    min-width: {MENU_ITEM_MIN_WIDTH}px;
}}

QMenu::item:selected {{
    background-color: {COLOR_MENU_ITEM_HOVER_BG};
    color: {COLOR_MENU_ITEM_HOVER_TEXT};
}}

QMenu::item:disabled {{
    color: {COLOR_TEXT_DISABLED};
}}

QMenu::separator {{
    height: 1px;
    margin: {MENU_SEPARATOR_MARGIN_Y}px {MENU_SEPARATOR_MARGIN_X}px;
    background: {COLOR_BORDER};
}}
"""


BUTTON_STYLE_PRESETS = {
    "primary": {
        "bg": BUTTON_PRIMARY_BG,
        "bg_hover": BUTTON_PRIMARY_BG_HOVER,
        "bg_pressed": BUTTON_PRIMARY_BG_PRESSED,
        "text": BUTTON_PRIMARY_TEXT,
        "text_hover": BUTTON_PRIMARY_TEXT,
        "border": BUTTON_PRIMARY_BORDER,
        "border_hover": BUTTON_PRIMARY_BORDER_HOVER,
        "border_pressed": BUTTON_PRIMARY_BORDER_PRESSED,
        "radius": BUTTON_PRIMARY_RADIUS,
        "height": BUTTON_PRIMARY_HEIGHT,
        "padding_y": BUTTON_PRIMARY_PADDING_Y,
        "padding_x": BUTTON_PRIMARY_PADDING_X,
        "font_weight": BUTTON_PRIMARY_FONT_WEIGHT,
        "font_size": BUTTON_PRIMARY_FONT_SIZE_PT,
        "text_transform": BUTTON_PRIMARY_TEXT_TRANSFORM,
        "disabled_bg": BUTTON_PRIMARY_DISABLED_BG,
        "disabled_text": BUTTON_PRIMARY_DISABLED_TEXT,
        "disabled_border": BUTTON_PRIMARY_DISABLED_BORDER,
    },
    "toolbar": {
        "bg": BUTTON_TOOLBAR_BG,
        "bg_hover": BUTTON_TOOLBAR_BG_HOVER,
        "bg_pressed": BUTTON_TOOLBAR_BG_PRESSED,
        "text": BUTTON_TOOLBAR_TEXT,
        "text_hover": BUTTON_TOOLBAR_TEXT,
        "border": BUTTON_TOOLBAR_BORDER,
        "border_hover": BUTTON_TOOLBAR_BORDER,
        "border_pressed": BUTTON_TOOLBAR_BORDER,
        "radius": BUTTON_TOOLBAR_RADIUS,
        "height": BUTTON_TOOLBAR_HEIGHT,
        "padding_y": BUTTON_TOOLBAR_PADDING_Y,
        "padding_x": BUTTON_TOOLBAR_PADDING_X,
        "font_weight": BUTTON_TOOLBAR_FONT_WEIGHT,
        "font_size": BUTTON_TOOLBAR_FONT_SIZE_PT,
        "text_transform": BUTTON_TOOLBAR_TEXT_TRANSFORM,
        "disabled_bg": BUTTON_TOOLBAR_DISABLED_BG,
        "disabled_text": BUTTON_TOOLBAR_DISABLED_TEXT,
        "disabled_border": BUTTON_TOOLBAR_DISABLED_BORDER,
    },
    "secondary": {
        "bg": BUTTON_SECONDARY_BG,
        "bg_hover": BUTTON_SECONDARY_BG_HOVER,
        "bg_pressed": BUTTON_SECONDARY_BG_PRESSED,
        "text": BUTTON_SECONDARY_TEXT,
        "text_hover": BUTTON_SECONDARY_TEXT_HOVER,
        "border": BUTTON_SECONDARY_BORDER,
        "border_hover": BUTTON_SECONDARY_BORDER_HOVER,
        "border_pressed": BUTTON_SECONDARY_BORDER_PRESSED,
        "radius": BUTTON_SECONDARY_RADIUS,
        "height": BUTTON_SECONDARY_HEIGHT,
        "padding_y": BUTTON_SECONDARY_PADDING_Y,
        "padding_x": BUTTON_SECONDARY_PADDING_X,
        "font_weight": BUTTON_SECONDARY_FONT_WEIGHT,
        "font_size": BUTTON_SECONDARY_FONT_SIZE_PT,
        "text_transform": BUTTON_SECONDARY_TEXT_TRANSFORM,
        "disabled_bg": BUTTON_SECONDARY_DISABLED_BG,
        "disabled_text": BUTTON_SECONDARY_DISABLED_TEXT,
        "disabled_border": BUTTON_SECONDARY_DISABLED_BORDER,
    },
}


GLOBAL_FONT_QSS = f"""
QWidget,
QMenuBar,
QMenu,
QTableView,
QTableWidget,
QHeaderView,
QPushButton,
QToolButton,
QLabel,
QLineEdit,
QComboBox,
QDateEdit,
QCheckBox,
QRadioButton,
QGroupBox,
QTabWidget,
QTreeView,
QListView,
QTextEdit,
QPlainTextEdit {{
    font-family: "{FONT_FAMILY}";
}}
"""


class _FixedPopupItemDelegate(QStyledItemDelegate):
    def __init__(self, row_height: int = 36, parent=None):
        super().__init__(parent)
        self._row_height = int(row_height)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self._row_height)
        return size


def _replace_hardcoded_font_family(qss: str) -> str:
    if not qss:
        return qss
    # Keep all existing font weights/sizes and only normalize the family source.
    updated = re.sub(r'"Overpass"', f'"{FONT_FAMILY}"', qss, flags=re.IGNORECASE)
    updated = re.sub(r"'Overpass'", f'"{FONT_FAMILY}"', updated, flags=re.IGNORECASE)
    return updated


def apply_global_font_to_window(window) -> None:
    if window is None:
        return

    app = QtWidgets.QApplication.instance()
    if app is not None:
        app_font = app.font()
        app_font.setFamily(FONT_FAMILY)
        app.setFont(app_font)

    try:
        merged_qss = f"{window.styleSheet()}\n{GLOBAL_FONT_QSS}" if window.styleSheet() else GLOBAL_FONT_QSS
        window.setStyleSheet(_replace_hardcoded_font_family(merged_qss))
    except RuntimeError:
        return

    for widget in [window, *window.findChildren(QtWidgets.QWidget)]:
        try:
            current_font = widget.font() or QFont()
            if current_font.family() != FONT_FAMILY:
                current_font.setFamily(FONT_FAMILY)
                widget.setFont(current_font)

            qss = widget.styleSheet()
            if qss:
                normalized = _replace_hardcoded_font_family(qss)
                if normalized != qss:
                    widget.setStyleSheet(normalized)
        except RuntimeError:
            continue


def apply_lineedit_style(line_edit: QLineEdit) -> None:
    if line_edit is None:
        return
    line_edit.setClearButtonEnabled(False)
    line_edit.setStyleSheet(ENTRY_QSS)


def apply_popup_list_style(view, row_height: int = 36) -> None:
    if view is None:
        return

    view.setStyleSheet(COMPLETER_POPUP_QSS)
    if hasattr(view, "setSpacing"):
        view.setSpacing(0)
    if hasattr(view, "setMouseTracking"):
        view.setMouseTracking(True)
    if hasattr(view, "setUniformItemSizes"):
        view.setUniformItemSizes(True)
    if hasattr(view, "setItemDelegate"):
        view.setItemDelegate(_FixedPopupItemDelegate(row_height=row_height, parent=view))


def apply_table_popup_style(table_view, row_height: int = 28) -> None:
    if table_view is None:
        return

    table_view.setStyleSheet(TABLE_POPUP_QSS)
    if hasattr(table_view, "verticalHeader") and table_view.verticalHeader() is not None:
        table_view.verticalHeader().setDefaultSectionSize(int(row_height))


def apply_popup_style_to_window(window, row_height: int = 36) -> None:
    for combo in window.findChildren(QtWidgets.QComboBox):
        try:
            apply_popup_list_style(combo.view(), row_height=row_height)
        except RuntimeError:
            continue


def apply_completer_popup_style_to_window(window, row_height: int = 36) -> None:
    for line_edit in window.findChildren(QLineEdit):
        try:
            completer = line_edit.completer()
            if completer is not None:
                apply_popup_list_style(completer.popup(), row_height=row_height)
        except RuntimeError:
            continue


def apply_combobox_style_to_window(window) -> None:
    for combo in window.findChildren(QtWidgets.QComboBox):
        try:
            combo.setStyleSheet(COMBOBOX_QSS)
            combo.setEditable(False)
        except RuntimeError:
            continue


def apply_dateedit_style_to_window(window) -> None:
    for date_edit in window.findChildren(QtWidgets.QDateEdit):
        try:
            date_edit.setStyleSheet(DATEEDIT_QSS)
        except RuntimeError:
            continue


def apply_entry_style_to_window(window) -> None:
    for line_edit in window.findChildren(QLineEdit):
        try:
            # Skip inner editors owned by spin boxes/date edits to avoid double borders.
            if isinstance(line_edit.parentWidget(), QtWidgets.QAbstractSpinBox):
                line_edit.setClearButtonEnabled(False)
                continue
            apply_lineedit_style(line_edit)
        except RuntimeError:
            continue


def apply_menu_style(menu) -> None:
    if menu is None:
        return

    menu.setMinimumWidth(MENU_MIN_WIDTH)
    menu.setStyleSheet(MENU_QSS)


def _button_qss(widget_selector: str, style_type: str) -> str:
    preset = BUTTON_STYLE_PRESETS.get((style_type or "").strip().lower())
    if not preset:
        return ""

    text_transform_rule = ""
    text_transform = str(preset.get("text_transform", "") or "").strip().lower()
    if text_transform in {"uppercase", "lowercase", "capitalize"}:
        text_transform_rule = f"text-transform: {text_transform};"

    return f"""
{widget_selector} {{
    background-color: {preset['bg']};
    border: {BORDER_SIZE}px solid {preset['border']};
    border-radius: {preset['radius']}px;
    min-height: {preset['height']}px;
    max-height: {preset['height']}px;
    color: {preset['text']};
    font: {preset['font_weight']} {preset['font_size']}pt \"{FONT_FAMILY}\";
    padding: {preset['padding_y']}px {preset['padding_x']}px;
    {text_transform_rule}
}}

{widget_selector}:hover {{
    background-color: {preset['bg_hover']};
    color: {preset['text_hover']};
    border-color: {preset['border_hover']};
}}

{widget_selector}:pressed {{
    background-color: {preset['bg_pressed']};
    border-color: {preset['border_pressed']};
}}

{widget_selector}:disabled {{
    background-color: {preset['disabled_bg']};
    color: {preset['disabled_text']};
    border-color: {preset['disabled_border']};
}}
"""


def apply_button_styles(window, widgets_map: dict | None = None) -> None:
    """Apply tokenized button styles by widget map.

    widgets_map format:
    {
        "widgetObjectName": ["QPushButton|QToolButton", "primary|secondary|toolbar"],
    }
    """
    if window is None or not widgets_map:
        return

    for widget_name, spec in widgets_map.items():
        if not isinstance(widget_name, str) or not widget_name.strip():
            continue

        widget_type_name = ""
        style_type = ""
        if isinstance(spec, (list, tuple)) and len(spec) >= 2:
            widget_type_name = str(spec[0] or "").strip()
            style_type = str(spec[1] or "").strip().lower()
        elif isinstance(spec, dict):
            widget_type_name = str(spec.get("widget_type") or spec.get("type") or "").strip()
            style_type = str(spec.get("widget_style_type") or spec.get("style") or "").strip().lower()
        else:
            continue

        if style_type not in BUTTON_STYLE_PRESETS:
            continue

        widget_cls = getattr(QtWidgets, widget_type_name, None)
        widget = None
        if widget_cls is not None and isinstance(widget_cls, type):
            widget = window.findChild(widget_cls, widget_name)
        if widget is None:
            widget = getattr(window, widget_name, None)
        if widget is None:
            continue

        if isinstance(widget, QtWidgets.QPushButton):
            selector = "QPushButton"
        elif isinstance(widget, QtWidgets.QToolButton):
            selector = "QToolButton"
        else:
            continue

        qss = _button_qss(selector, style_type)
        if not qss:
            continue

        try:
            widget.setStyleSheet(qss)
        except RuntimeError:
            continue


def _iter_target_widgets(window, widget_name: str, widget_cls):
    if window is None or widget_cls is None:
        return []

    if widget_name.startswith("__all"):
        widgets = []
        if isinstance(window, widget_cls):
            widgets.append(window)
        widgets.extend(window.findChildren(widget_cls))
        return widgets

    widget = window.findChild(widget_cls, widget_name)
    if widget is None:
        widget = getattr(window, widget_name, None)

    if widget is None:
        return []

    return [widget]


def _normalize_style_spec(spec):
    widget_type_name = ""
    style_type = ""
    options = {}

    if isinstance(spec, (list, tuple)) and len(spec) >= 2:
        widget_type_name = str(spec[0] or "").strip()
        style_type = str(spec[1] or "").strip().lower()
        if len(spec) >= 3 and isinstance(spec[2], dict):
            options = dict(spec[2])
    elif isinstance(spec, dict):
        widget_type_name = str(spec.get("widget_type") or spec.get("type") or "").strip()
        style_type = str(spec.get("widget_style_type") or spec.get("style") or "").strip().lower()
        opts = spec.get("options") or {}
        if isinstance(opts, dict):
            options = dict(opts)

    return widget_type_name, style_type, options


def _apply_style_to_widget(window, widget, style_type: str, options: dict, default_row_height: int):
    if widget is None or not style_type:
        return

    row_height = int(options.get("row_height", default_row_height) or default_row_height)

    if style_type == "global_font":
        apply_global_font_to_window(window)
        return

    if style_type == "entry":
        if isinstance(widget, QLineEdit):
            if isinstance(widget.parentWidget(), QtWidgets.QAbstractSpinBox):
                widget.setClearButtonEnabled(False)
                return
            apply_lineedit_style(widget)
        return

    if style_type == "combobox":
        if isinstance(widget, QtWidgets.QComboBox):
            widget.setStyleSheet(COMBOBOX_QSS)
            widget.setEditable(False)
        return

    if style_type == "dateedit":
        if isinstance(widget, QtWidgets.QDateEdit):
            widget.setStyleSheet(DATEEDIT_QSS)
        return

    if style_type == "popup_list":
        if isinstance(widget, QtWidgets.QComboBox):
            apply_popup_list_style(widget.view(), row_height=row_height)
        else:
            apply_popup_list_style(widget, row_height=row_height)
        return

    if style_type == "completer_popup":
        if isinstance(widget, QLineEdit):
            completer = widget.completer()
            if completer is not None:
                apply_popup_list_style(completer.popup(), row_height=row_height)
        return

    if style_type == "table_popup":
        apply_table_popup_style(widget, row_height=row_height)
        return

    if style_type == "menu":
        apply_menu_style(widget)
        return

    if style_type in BUTTON_STYLE_PRESETS:
        if isinstance(widget, QtWidgets.QPushButton):
            selector = "QPushButton"
        elif isinstance(widget, QtWidgets.QToolButton):
            selector = "QToolButton"
        else:
            return
        qss = _button_qss(selector, style_type)
        if qss:
            widget.setStyleSheet(qss)


def apply_styles_from_map(window, widgets_map: dict | None = None, default_row_height: int = 36) -> None:
    """Apply styles from one map for all supported widget style types."""
    if window is None or not widgets_map:
        return

    for widget_name, spec in widgets_map.items():
        if not isinstance(widget_name, str) or not widget_name.strip():
            continue

        widget_type_name, style_type, options = _normalize_style_spec(spec)
        if not widget_type_name or not style_type:
            continue

        widget_cls = getattr(QtWidgets, widget_type_name, None)
        if widget_cls is None or not isinstance(widget_cls, type):
            continue

        targets = _iter_target_widgets(window, widget_name.strip(), widget_cls)
        for widget in targets:
            try:
                _apply_style_to_widget(
                    window,
                    widget,
                    style_type=style_type,
                    options=options,
                    default_row_height=default_row_height,
                )
            except RuntimeError:
                continue


def _default_style_map(row_height: int) -> dict:
    return {
        "__window__": ["QWidget", "global_font"],
        "__all_lineedits__": ["QLineEdit", "entry"],
        "__all_comboboxes__": ["QComboBox", "combobox"],
        "__all_dateedits__": ["QDateEdit", "dateedit"],
        "__all_combobox_popups__": ["QComboBox", "popup_list", {"row_height": int(row_height)}],
        "__all_completer_popups__": ["QLineEdit", "completer_popup", {"row_height": int(row_height)}],
    }


def apply_input_styles_to_window(
    window,
    row_height: int = 36,
    button_widgets_map: dict | None = None,
    widget_styles_map: dict | None = None,
) -> None:
    merged_map = _default_style_map(row_height=row_height)

    if widget_styles_map:
        merged_map.update(widget_styles_map)
    elif button_widgets_map:
        merged_map.update(button_widgets_map)

    apply_styles_from_map(window, merged_map, default_row_height=row_height)
