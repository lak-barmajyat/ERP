from PyQt5.QtCore import Qt, QSortFilterProxyModel, QTimer, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QListView
)

class SmartFilterComboBox(QComboBox):
    """
    QComboBox متقدم:
    - قابل للكتابة والاختيار
    - يفتح القائمة تلقائياً عند التركيز أو الضغط
    - فلترة لحظية أثناء الكتابة (Proxy Model)
    - ستايل حديث ونظيف
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1) إعدادات أساسية
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)   # لا تضف نصوص جديدة تلقائياً للعناصر
        self.setMaxVisibleItems(10)

        # 2) View مخصصة (لتجميل القائمة والتحكم)
        view = QListView()
        view.setUniformItemSizes(True)
        self.setView(view)

        # 3) نموذج البيانات + proxy للفلترة
        self._source_model = QStandardItemModel(self)
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setFilterKeyColumn(0)

        # اربط الـ combobox بالـ proxy
        self.setModel(self._proxy_model)

        # 4) Debounce لتحديث الفلترة بسلاسة
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(60)  # ms (تقدر تزود/تقلل حسب رغبتك)
        self._filter_timer.timeout.connect(self._apply_filter)

        # 5) ربط أحداث الكتابة/التركيز
        self.lineEdit().textEdited.connect(self._on_text_edited)
        self.lineEdit().installEventFilter(self)

        # 6) ستايل حديث
        self._apply_modern_style()

    # ---------------------------
    # API نظيفة لتغذية البيانات
    # ---------------------------
    def set_items(self, items, *, keep_current_text=True):
        """
        items: list[str]
        keep_current_text: يحافظ على النص المكتوب أثناء تحديث القائمة
        """
        current = self.currentText() if keep_current_text else ""

        self._source_model.clear()
        for text in items:
            if not text:
                continue
            it = QStandardItem(text)
            it.setEditable(False)
            self._source_model.appendRow(it)

        # إعادة تطبيق الفلترة حسب النص الحالي
        self.setEditText(current)
        self._apply_filter()

    # ---------------------------
    # منطق الفلترة
    # ---------------------------
    def _on_text_edited(self, _):
        self._filter_timer.start()  # debounce
        # افتح القائمة فوراً أثناء الكتابة ليشوف النتائج مباشرة
        if not self.view().isVisible():
            self.showPopup()

    def _apply_filter(self):
        text = self.lineEdit().text().strip()
        # فلترة "contains" (أي مكان داخل النص) بدل يبدأ بـ
        self._proxy_model.setFilterFixedString("")  # reset بسيط
        self._proxy_model.setFilterRegularExpression(text)

        # إذا ما في نتائج، لا تغلق بالضرورة، بس تقدر تتحكم هنا
        if self._proxy_model.rowCount() > 0:
            if not self.view().isVisible():
                self.showPopup()

    # ---------------------------
    # فتح القائمة عند التركيز/الضغط
    # ---------------------------
    def eventFilter(self, obj, event):
        if obj is self.lineEdit():
            if event.type() == QEvent.FocusIn:
                # عند دخول المؤشر (Focus) افتح القائمة مباشرة
                QTimer.singleShot(0, self.showPopup)
            elif event.type() == QEvent.MouseButtonPress:
                # عند الضغط داخل خانة الكتابة افتح القائمة فوراً
                QTimer.singleShot(0, self.showPopup)
            elif event.type() == QEvent.KeyPress:
                # لو ضغط سهم لأسفل افتح القائمة
                if event.key() in (Qt.Key_Down,):
                    QTimer.singleShot(0, self.showPopup)
        return super().eventFilter(obj, event)

    # ---------------------------
    # ستايل حديث (QSS)
    # ---------------------------
    def _apply_modern_style(self):
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid rgba(0,0,0,0.15);
                border-radius: 10px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid rgba(60, 130, 255, 0.9);
            }
            QComboBox::drop-down {
                border: 0px;
                width: 28px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }

            /* lineEdit داخل combobox */
            QComboBox QLineEdit {
                border: 0px;
                padding: 0px;
                background: transparent;
            }

            /* قائمة العناصر */
            QAbstractItemView {
                border: 1px solid rgba(0,0,0,0.12);
                border-radius: 12px;
                padding: 6px;
                background: white;
                outline: 0;
                selection-background-color: rgba(60, 130, 255, 0.15);
            }
            QAbstractItemView::item {
                padding: 10px 10px;
                border-radius: 10px;
                margin: 2px 2px;
            }
            QAbstractItemView::item:selected {
                background: rgba(60, 130, 255, 0.18);
            }
            QAbstractItemView::item:hover {
                background: rgba(0,0,0,0.04);
            }
        """)

# ---------------------------
# مثال استخدام مع بيانات قاعدة البيانات
# ---------------------------

def build_clients_list(session, Tiers, select):
    """
    دالة نظيفة لجلب أسماء العملاء (مع تنظيف النتائج)
    - تتجنب None
    - تتجنب الفراغات
    - تتجنب التكرار مع الحفاظ على الترتيب
    """
    query = (
        select(Tiers.nom_tiers)
        .where(Tiers.type_tiers == "CLIENT")
        .order_by(Tiers.nom_tiers)
    )
    names = session.execute(query).scalars().all()

    cleaned = []
    seen = set()
    for name in names:
        if not name:
            continue
        name = str(name).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        cleaned.append(name)
    return cleaned

# ---------------------------
# Demo UI (اختياري للتجربة)
# ---------------------------

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = QWidget()
    layout = QVBoxLayout(w)

    layout.addWidget(QLabel("اختر/اكتب اسم العميل:"))

    combo = SmartFilterComboBox()
    combo.set_items([
        "Ahmed Trading", "Alpha Client", "Beta Services",
        "Client One", "Client Two", "Delta Market", "Zeta Store"
    ])
    layout.addWidget(combo)

    w.resize(520, 140)
    w.show()
    sys.exit(app.exec_())