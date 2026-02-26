import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class SelectDocTypeDialog(QDialog):
    def __init__(self):
        super(SelectDocTypeDialog, self).__init__()
        loadUi(resource_path("select_doc_type.ui"), self)
        
        # Connect buttons
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        # Dictionary to map radio buttons to document types
        self.doc_type_map = {
            self.radioDevis: "Devis",
            self.radioBonCommande: "Bon de commande",
            self.radioPrepLivraison: "Préparation de livraison",
            self.radioBonLivraison: "Bon de livraison",
            self.radioBonRetour: "Bon de retour",
            self.radioBonAvoirFinancier: "Bon d'avoir financier",
            self.radioFacture: "Facture",
            self.radioFactureRetour: "Facture de retour",
            self.radioFactureAvoir: "Facture d'avoir"
        }
    
    def get_selected_doc_type(self):
        """Returns the selected document type"""
        for radio, doc_type in self.doc_type_map.items():
            if radio.isChecked():
                return doc_type
        return None


def main():
    """Main function for testing the SelectDocTypeDialog"""
    app = QApplication(sys.argv)
    dialog = SelectDocTypeDialog()
    
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        selected_type = dialog.get_selected_doc_type()
        print(f"Selected document type: {selected_type}")
    else:
        print("Dialog cancelled")
    
    sys.exit()


if __name__ == "__main__":
    main()
