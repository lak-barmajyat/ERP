import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
import os
from program.themes.shared_input_popup_style import (
    COLOR_BG,
    COLOR_TEXT,
    FONT_FAMILY,
    FONT_SIZE_PT,
    FONT_WEIGHT,
    apply_input_styles_to_window,
)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class SelectDocTypeDialog(QDialog):
    def __init__(self, *, domain_id: int = 1):
        super(SelectDocTypeDialog, self).__init__()
        loadUi(resource_path("select_doc_type.ui"), self)

        # Base dialog look from the shared token system (colors + typography).
        self.setStyleSheet(
            f"""
QDialog#Dialog {{
    background-color: {COLOR_BG};
}}

QLabel, QRadioButton {{
    color: {COLOR_TEXT};
    font: {FONT_WEIGHT} {FONT_SIZE_PT}pt \"{FONT_FAMILY}\";
}}

QRadioButton::indicator {{
    width: 14px;
    height: 14px;
}}
""".strip()
        )

        apply_input_styles_to_window(
            self,
            row_height=36,
            widget_styles_map={
                "okButton": ["QPushButton", "primary"],
                "cancelButton": ["QPushButton", "secondary"],
            },
        )

        try:
            self.domain_id = int(domain_id or 1)
        except (TypeError, ValueError):
            self.domain_id = 1
        
        # Connect buttons
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        # Domain-aware first option: DV (Ventes) vs DA (Achats)
        self._primary_code = "DA" if self.domain_id == 2 else "DV"
        primary_label = "Demande d'achat" if self._primary_code == "DA" else "Devis"
        if hasattr(self, "radioDevis"):
            self.radioDevis.setText(primary_label)

    def get_current_doc_type(self):
        """Returns the selected document type"""
        if hasattr(self, "radioDevis") and self.radioDevis.isChecked():
            return self._primary_code
        if hasattr(self, "radioBonCommande") and self.radioBonCommande.isChecked():
            return "BC"
        if hasattr(self, "radioBonLivraison") and self.radioBonLivraison.isChecked():
            return "BL"
        if hasattr(self, "radioFacture") and self.radioFacture.isChecked():
            return "FA"
        if hasattr(self, "radioFactureAvoir") and self.radioFactureAvoir.isChecked():
            return "AV"
        return self._primary_code


def main():
    """Main function for testing the SelectDocTypeDialog"""
    app = QApplication(sys.argv)
    dialog = SelectDocTypeDialog()
    
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        selected_type = dialog.get_current_doc_type()
        print(f"Selected document type: {selected_type}")
    else:
        print("Dialog cancelled")
    
    sys.exit()


if __name__ == "__main__":
    main()
