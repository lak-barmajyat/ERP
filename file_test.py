import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

class FilterableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setEditable(True)
        self.full_list = []
        self.last_text = ""
        
        self.lineEdit().textChanged.connect(self.filter_items)
        self.activated.connect(self.on_activated)
    
    def add_items(self, items):
        self.full_list = items[:]
        self.update_combo_box(items)
    
    def update_combo_box(self, items):
        # Block signals to avoid recursion
        self.lineEdit().blockSignals(True)
        self.blockSignals(True)
        
        # Clear and add new items. The line edit text is unchanged.
        self.clear()
        if items:
            self.addItems(items)
        
        # Re-enable signals
        self.blockSignals(False)
        self.lineEdit().blockSignals(False)
    
    def filter_items(self, text):
        if text == self.last_text:
            return
        self.last_text = text
        
        if not text:
            filtered = self.full_list
        else:
            filtered = [item for item in self.full_list 
                        if item.lower().startswith(text.lower())]
        
        self.update_combo_box(filtered)
        
        # Open the popup if there are items to show
        if filtered:
            QTimer.singleShot(0, self.open_popup_and_refocus)
        else:
            self.hidePopup()
    
    def open_popup_and_refocus(self):
        # Open popup only if not already visible
        if not self.view().isVisible():
            self.showPopup()
        # Ensure line edit keeps focus
        self.lineEdit().setFocus()
    
    def on_activated(self, index):
        # When an item is selected from the dropdown
        selected_text = self.itemText(index)
        
        # Block signals while we set the text
        self.lineEdit().blockSignals(True)
        self.setEditText(selected_text)
        self.lineEdit().blockSignals(False)
        
        self.last_text = selected_text
        self.hidePopup()
        
        # Keep focus on the line edit
        self.lineEdit().setFocus()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typeable & Filterable ComboBox")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Type to filter and auto‑open the dropdown:"))
        
        self.combo = FilterableComboBox()
        items = [
            "Apple", "Apricot", "Banana", "Blueberry", "Cherry",
            "Cranberry", "Grape", "Grapefruit", "Lemon", "Lime",
            "Orange", "Peach", "Pear", "Pineapple", "Raspberry",
            "Strawberry", "Watermelon"
        ]
        self.combo.add_items(items)
        
        layout.addWidget(self.combo)
        self.setLayout(layout)
        
        self.combo.currentTextChanged.connect(self.on_selection_changed)
    
    def on_selection_changed(self, text):
        print(f"Selected: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())