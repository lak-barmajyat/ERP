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
        /* 1. الحاوية الرئيسية للتقويم */
        QCalendarWidget QWidget {{
            background-color: #FDFDFD; /* var(--c-bg-tertiary) */
            font-family: "Inter", "Segoe UI";
        }}

        /* 2. شريط التنقل العلوي (المكان الذي يوجد فيه اسم الشهر والأسهم) */
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: #FDFDFD;
            border-bottom: 1px solid #EAEBEC;
        }}

        /* 3. تنسيق أسهم التنقل */
        QCalendarWidget QToolButton {{
            color: #1F1F25; /* var(--c-text-primary) */
            background-color: white;
            border-radius: 8px;
            margin: 5px;
            width: 75px;
            height: 20px;
            icon-size: 20px;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: #EAEBEC;
        }}

        /* 4. أسماء الأيام (السبت، الأحد...) */
        QCalendarWidget QWidget#qt_calendar_calendarview {{
            outline: 0;
            selection-background-color: #008FFD; /* var(--c-theme-primary) */
            selection-color: white;
        }}

        /* 5. تنسيق الأيام داخل التقويم */
        QCalendarWidget QAbstractItemView:enabled {{
            color: #1F1F25;
            font-weight: 600;
            selection-background-color: #008FFD;
            selection-color: white;
            background-color: white;
        }}

        /* الأيام "الباهتة" أو أيام الشهر السابق/القادم */
        QCalendarWidget QAbstractItemView:disabled {{
            color: #999FA6; /* var(--c-text-secondary) */
        }}

        /* 6. تنسيق القوائم المنسدلة لاختيار الشهر والسنة */
        QCalendarWidget QMenu {{
            background-color: white;
            color: #1F1F25;
            border: 1px solid #EAEBEC;
            height: 150px;
            width: 100px;
        }}

        QCalendarWidget QSpinBox {{
            width: 40px;
            height: 5px;
            font-size: 15px;
            background: transparent;
            color: #1F1F25;
            selection-background-color: #CBE8FF;
            selection-color: #000000;
        }}
        /* 1. تنسيق شريط التمرير العمودي بالكامل */
        QScrollBar:vertical {{
            border: none;
            background: transparent; /* خلفية شفافة لتبدو عصرية */
            width: 10px; /* عرض نحيف */
            margin: 0px 0px 0px 0px;
        }}

        /* 2. المقبض (الجزء الذي يتحرك) */
        QScrollBar::handle:vertical {{
            background: #cbd5e1; /* لون رمادي فاتح هادئ */
            min-height: 10px;
            border-radius: 5px; /* حواف دائرية كاملة */
            margin: 2px; /* ترك مسافة بسيطة عن الحواف */
        }}

        /* تغيير لون المقبض عند تمرير الماوس */
        QScrollBar::handle:vertical:hover {{
            background: #94a3b8; /* لون أغمق قليلاً عند التفاعل */
        }}

        /* 3. إخفاء أزرار الأسهم (للحصول على مظهر نظيف) */
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}

        /* 4. إخفاء المساحة المتبقية من المسار (Track) */
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        /* --- تكرار التنسيق للشريط الأفقي --- */
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: #cbd5e1;
            min-width: 30px;
            border-radius: 5px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: #94a3b8;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}
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

        QPushButton[transparent="true"] {{
            background-color: transparent;
            color: {C['TRANSPARENT_BUTTON']};
            border: 0px solid {C['PRIMARY']};
        }}

        QPushButton[transparent="true"]:hover {{
            background-color: {C['PRIMARY_SOFT']};
            color: {C['TRANSPARENT_BUTTON']};
        }}

        QPushButton[transparent="true"]:pressed {{
            background-color: {C['PRIMARY']};
            color: {C['TRANSPARENT_BUTTON']};
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
            image: url("program/assets/global/down_blue_arrow.svg");
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
    @staticmethod
    def apply_text_color_by_background(button):
        """
        Check if button has transparent background and apply appropriate text color.
        Transparent background → Black text
        Regular background → White text
        """
        current_style = button.styleSheet()
        
        # Check if background is transparent
        is_transparent = (
            'background-color: transparent' in current_style.lower() or
            'background: transparent' in current_style.lower() or
            'background-color:transparent' in current_style.lower() or
            'background:transparent' in current_style.lower()
        )
        
        if is_transparent:
            # Keep existing style but ensure text is black
            if 'color:' not in current_style.lower():
                button.setStyleSheet(current_style + "\ncolor: #000000;")
            elif 'color: #000000' not in current_style and 'color:#000000' not in current_style:
                # Replace color with black
                import re
                new_style = re.sub(r'color:\s*[^;]+;?', 'color: #000000;', current_style, flags=re.IGNORECASE)
                button.setStyleSheet(new_style)
        else:
            # Button has background, ensure text is white
            if 'color:' not in current_style.lower():
                button.setStyleSheet(current_style + "\ncolor: #FFFFFF;")
            elif 'color: #ffffff' not in current_style.lower() and 'color:#ffffff' not in current_style.lower():
                # Replace color with white
                import re
                new_style = re.sub(r'color:\s*[^;]+;?', 'color: #FFFFFF;', current_style, flags=re.IGNORECASE)
                button.setStyleSheet(new_style)
        
        return is_transparent