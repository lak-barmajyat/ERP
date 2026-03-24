import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

class NouveauClientWindow(QtWidgets.QDialog):
    def __init__(self):
        super(NouveauClientWindow, self).__init__()
        
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "nouveau_client.ui")
        uic.loadUi(ui_path, self)
        
        # Frameless window hint for custom title bar design
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Custom logic for the close button
        self.btnClose.clicked.connect(self.close)
        
        # Custom logic for Annuler button
        self.btnAnnuler.clicked.connect(self.close)
        
        # Enable dragging from the header
        self._dragging = False
        self._drag_position = None
        self.headerFrame.mousePressEvent = self.header_mousePressEvent
        self.headerFrame.mouseMoveEvent = self.header_mouseMoveEvent
        self.headerFrame.mouseReleaseEvent = self.header_mouseReleaseEvent

    # Draggable title bar logic
    def header_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.pos()
            event.accept()

    def header_mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def header_mouseReleaseEvent(self, event):
        self._dragging = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply global palette for better anti-aliasing if needed, but styling is in .ui
    window = NouveauClientWindow()
    window.show()
    
    sys.exit(app.exec_())
