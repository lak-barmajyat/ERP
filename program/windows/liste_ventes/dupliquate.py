import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from program.themes.shared_input_popup_style import apply_global_font_to_window

class DupliquateWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DupliquateWindow, self).__init__()
        
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "dupliquate.ui")
        uic.loadUi(ui_path, self)
        apply_global_font_to_window(self)
        
        # In a real app, logic would be hooked up here
        self.btnDlgClose.clicked.connect(self.close)
        self.btnAnnuler.clicked.connect(self.close)
        self.btnConfirmer.clicked.connect(self.confirm_action)
        
        # Toggle states for mode buttons (styling handled in QSS or extended logic)
        self.btnModeDupliquer.clicked.connect(lambda: self.set_mode("dupliquer"))
        self.btnModeRemplacer.clicked.connect(lambda: self.set_mode("remplacer"))

    def set_mode(self, mode):
        # Very basic check, active mode could be styled here if needed
        if mode == "dupliquer":
            self.btnModeDupliquer.setStyleSheet("background-color: #eff6ff; border: 2px solid #1d4ed8; color: #1d4ed8; border-radius: 4px; padding: 12px; font-size: 12px; font-weight: bold;")
            self.btnModeRemplacer.setStyleSheet("background-color: transparent; border: 1px solid #e2e8f0; color: #64748b; border-radius: 4px; padding: 12px; font-size: 12px; font-weight: bold;")
        else:
            self.btnModeRemplacer.setStyleSheet("background-color: #eff6ff; border: 2px solid #1d4ed8; color: #1d4ed8; border-radius: 4px; padding: 12px; font-size: 12px; font-weight: bold;")
            self.btnModeDupliquer.setStyleSheet("background-color: transparent; border: 1px solid #e2e8f0; color: #64748b; border-radius: 4px; padding: 12px; font-size: 12px; font-weight: bold;")

    def confirm_action(self):
        print(f"Action confirmed. Client: {{self.comboClient.currentText()}}, Doc: {{self.comboDocType.currentText()}}, Date: {{self.dateTarget.date().toString('yyyy-MM-dd')}}")
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DupliquateWindow()
    window.show()
    
    if os.environ.get("AUTO_TEST") == "1":
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, app.quit)
        
    sys.exit(app.exec_())
