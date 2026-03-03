from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DynamicMessageBox(QDialog):
    def __init__(self, message_type="info", message_text="", parent=None):
        super().__init__(parent)

        # =============================
        # Window Setup
        # =============================
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(400, 200)

        # =============================
        # Main Layout
        # =============================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.frame = QLabel()
        self.frame.setObjectName("mainFrame")
        self.frame.setStyleSheet("""
            #mainFrame {
                background-color: #fefefe;
                border-radius: 15px;
            }
        """)

        content_layout = QVBoxLayout(self.frame)
        content_layout.setContentsMargins(25, 25, 25, 20)
        content_layout.setSpacing(20)

        # =============================
        # Icon and Title
        # =============================
        icon_title_layout = QHBoxLayout()
        icon_title_layout.setSpacing(15)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Title
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            color: black;
            font-size: 16px;
            font-weight: 600;
        """)

        # Set icon and title based on message type
        if message_type == "error":
            self.icon_label.setText("❌")
            self.title_label.setText("Erreur")
            icon_color = "#ef233c"
        elif message_type == "warning":
            self.icon_label.setText("⚠️")
            self.title_label.setText("Attention")
            icon_color = "#ff9f1c"
        elif message_type == "info":
            self.icon_label.setText("ℹ️")
            self.title_label.setText("Information")
            icon_color = "#3a86ff"
        elif message_type == "success":
            self.icon_label.setText("✅")
            self.title_label.setText("Succès")
            icon_color = "#2a9d8f"
        elif message_type == "question":
            self.icon_label.setText("❓")
            self.title_label.setText("Confirmation")
            icon_color = "#3a86ff"
        else:
            self.icon_label.setText("ℹ️")
            self.title_label.setText("Information")
            icon_color = "#3a86ff"

        self.icon_label.setStyleSheet(f"""
            color: {icon_color};
            font-size: 28px;
        """)

        icon_title_layout.addWidget(self.icon_label)
        icon_title_layout.addWidget(self.title_label)
        icon_title_layout.addStretch()

        # =============================
        # Message Text
        # =============================
        self.message_label = QLabel(message_text)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignLeft)
        self.message_label.setStyleSheet("""
            color: #2b2d42;
            font-size: 14px;
            padding: 5px 0;
        """)

        # =============================
        # Buttons
        # =============================
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.yes_button = QPushButton("Oui")
        self.no_button = QPushButton("Non")
        self.cancel_button = QPushButton("Annuler")

        for btn in [self.ok_button, self.yes_button, self.no_button, self.cancel_button]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(35)
            btn.setFixedWidth(90)

        # OK Button Style
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3a86ff;
                color: white;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2667cc;
            }
        """)

        # Yes Button Style
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #2a9d8f;
                color: white;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #21867a;
            }
        """)

        # No Button Style
        self.no_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3d5c;
                color: white;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2b2d42;
            }
        """)

        # Cancel Button Style
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        # Configure buttons based on message type
        if message_type == "question":
            buttons_layout.addWidget(self.yes_button)
            buttons_layout.addWidget(self.no_button)
            buttons_layout.addWidget(self.cancel_button)
            self.yes_button.clicked.connect(lambda: self.done(QMessageBox.Yes))
            self.no_button.clicked.connect(lambda: self.done(QMessageBox.No))
            self.cancel_button.clicked.connect(lambda: self.done(QMessageBox.Cancel))
        else:
            buttons_layout.addWidget(self.ok_button)
            self.ok_button.clicked.connect(self.accept)

        # =============================
        # Add Widgets
        # =============================
        content_layout.addLayout(icon_title_layout)
        content_layout.addWidget(self.message_label)
        content_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.frame)

        # =============================
        # Shadow
        # =============================
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setYOffset(2)
        shadow.setXOffset(2)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.frame.setGraphicsEffect(shadow)


# =============================
# Dynamic MessageBox Function
# =============================
def show_message_box(message_type="info", message_text="", parent=None):
    """
    Display a dynamic message box
    
    Args:
        message_type: "error", "warning", "info", "success", "question"
        message_text: The message to display (in French)
        parent: Parent widget
    
    Returns:
        QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel, or QMessageBox.Ok equivalent
    """
    dialog = DynamicMessageBox(message_type, message_text, parent)
    return dialog.exec_()


# Add this at the end of your file
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Test different message types
    show_message_box("info", "Ceci est un message d'information.")
    show_message_box("success", "Opération réussie!")
    show_message_box("warning", "Attention: fichier non trouvé.")
    show_message_box("error", "Erreur de connexion.")
    
    # Test question with result
    result = show_message_box("question", "Voulez-vous continuer?")
    if result == QMessageBox.Yes:
        print("Utilisateur a cliqué Oui")
    elif result == QMessageBox.No:
        print("Utilisateur a cliqué Non")
    elif result == QMessageBox.Cancel:
        print("Utilisateur a cliqué Annuler")
    
    sys.exit(app.exec_())
