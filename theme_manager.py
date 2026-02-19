import json
import os


class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.current_theme = None

    def load_theme(self, theme_name):
        base_path = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(base_path, "program", "themes", f"{theme_name}.json")

        with open(theme_path, "r") as f:
            colors = json.load(f)

        self.app.setStyleSheet(self.build_stylesheet(colors))
        self.current_theme = theme_name

    def build_stylesheet(self, C):
        return f"""
        QWidget {{
            background-color: {C['BG_MAIN']};
            color: {C['TEXT_PRIMARY']};
            font-family: Tajawal-Bold;
            font-size: 12px;
        }}

        QFrame, QGroupBox {{
            background-color: {C['CARD']};
            border: 1px solid {C['BORDER']};
            border-radius: 6px;
        }}

        QPushButton {{
            background-color: {C['PRIMARY']};
            color: {C['PRIMARY_TEXT']};
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-family: Tajawal-Bold;
            font-size: 13px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {C['PRIMARY_HOVER']};
        }}

        QPushButton:pressed {{
            background-color: {C['PRIMARY_PRESSED']};
        }}

        QLineEdit, QTextEdit {{
            background-color: {C['CARD']};
            border: 1px solid {C['BORDER']};
            padding: 5px;
            border-radius: 4px;
        }}

        QComboBox {{
            background-color: {C['CARD']};
            border: 1px solid {C['BORDER']};
            padding: 5px;
            border-radius: 4px;
            color: {C['TEXT_PRIMARY']};
            font-size: 12px;
        }}

        QComboBox:hover {{
            border: 1px solid {C['PRIMARY']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: url(:/assets/program/assets/global/down_blue_arrow.svg);
            width: 12px;
            height: 12px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {C['CARD']};
            border: 1px solid {C['BORDER']};
            selection-background-color: {C['PRIMARY']};
            color: {C['TEXT_PRIMARY']};
        }}

        QToolButton {{
            padding: 20px;
            spacing: 0px;
            font-size: 12px;
            font-weight: bold;
            color: #1e293b;
            background-color: #e2e8f0;
            border-radius: 10px;
            border: none;
        }}
        QToolButton:hover {{
            background-color: #cbd5e1;
        }}
        QToolButton:pressed {{
            background-color: #94a3b8;
        }}

        QHeaderView {{
            background-color: {C['PRIMARY_SOFT']};
            border: none;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
        }}

        QHeaderView::section {{
            background-color: {C['PRIMARY_SOFT']};
            color: {C['TEXT_PRIMARY']};
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            padding-left: 0px;
            padding-right: 0px;
            border-radius: 0px;
            border: none;
            border-right: 1px solid {C['DIVIDER']};
        }}

        QHeaderView::section:last {{
            border-right: none;
        }}

        QTableWidget {{
            background-color: {C['CARD']};
            border: 1px solid {C['BORDER']};
            border-radius: 12px;
            gridline-color: transparent;
            outline: 0;
            padding: 10px;
        }}

        QTableWidget::item {{
            color: {C['TEXT_PRIMARY']};
            padding-left: 25px;
            border-bottom: 1px solid {C['ROW_ALT']};
        }}

        QTableWidget::item:selected {{
            background-color: {C['PRIMARY']};
            color: {C['PRIMARY_TEXT']};
        }}

        QTableWidget::item:hover {{
            background-color: {C['PRIMARY_SOFT']};
        }}

        QTableWidget::item:alternate {{
            background-color: {C['ROW_ALT']};
        }}

        QTableWidget QTableCornerButton::section {{
            background-color: {C['PRIMARY_SOFT']};
            border: none;
            border-top-left-radius: 10px;
        }}

        QLabel{{
            font-size: 14px;
            font-weight: bold;
            color: {C['TEXT_PRIMARY']};
            border: none;
        }}
        """
