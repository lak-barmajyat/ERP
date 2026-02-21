import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ClientsFacturesWindow(QMainWindow):
    def __init__(self):
        super(ClientsFacturesWindow, self).__init__()
        loadUi(resource_path("clients_factures.ui"), self)
        
        # Set all columns to Fixed mode to match input fields exactly
        # Widths match the input fields above the table
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        self.tableWidget.setColumnWidth(0, 225)  # Reference d'Article
        self.tableWidget.setColumnWidth(1, 885)  # Designation (matches lineEdit_9)
        self.tableWidget.setColumnWidth(2, 115)  # P.U.H.T
        self.tableWidget.setColumnWidth(3, 115)  # P.T.T.C
        self.tableWidget.setColumnWidth(4, 115)  # Qte
        self.tableWidget.setColumnWidth(5, 115)  # Taxe (matches lineEdit_12)
        self.tableWidget.setColumnWidth(6, 115)  # Total TTC (matches lineEdit_10)


        # Set transparent property for buttons with transparent background
        self.annule.setProperty("transparent", "true")  # Annuler
        self.suprimer.setProperty("transparent", "true")  # Supprimer
        self.fermer.setProperty("transparent", "true")  # Fermer
    
    def setup_table(self):
        """Initialize the table widget"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)
 

def main():
    """Main function for testing the ClientsFacturesWindow"""
    app = QApplication(sys.argv)
    window = ClientsFacturesWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
