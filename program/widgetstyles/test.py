"""
Simple test for apply_lineedit_combo_style and LineEditAutoComplete.
Run from project root: python program/widgetstyles/test.py
Or: python -m program.widgetstyles.test
"""
import sys
import os

# Add project root so 'program' can be imported when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton

from program.widgetstyles.lineedit_combo_style import (
    apply_lineedit_combo_style,
    LineEditAutoComplete,
)


def main():
    app = QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("LineEdit Combo Style Test")
    layout = QVBoxLayout(w)

    # 1. Style-only LineEdit (no autocomplete)
    le_style_only = QLineEdit()
    le_style_only.setPlaceholderText("Style only - no suggestions")
    apply_lineedit_combo_style(le_style_only)
    layout.addWidget(le_style_only)

    # 2. Full LineEdit with autocomplete (same show as old combo)
    le_autocomplete = QLineEdit()
    le_autocomplete.setPlaceholderText("Client (with autocomplete)")
    ac = LineEditAutoComplete(le_autocomplete, w)
    ac.set_items([
        "Ahmed Lak", "Aboubakr Laktawi", "Fatima Laktawi",
        "Mossab Laktawi", "Elhocine Laktawi",
        "Client Casablanca", "Client Rabat", "Client Agadir",
    ])
    layout.addWidget(le_autocomplete)

    btn = QPushButton("Open suggestions")
    btn.clicked.connect(ac.open_popup)
    layout.addWidget(btn)

    w.resize(400, 180)
    le_style_only.setFocus()  # Start with focus on style-only so both are easy to use
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
