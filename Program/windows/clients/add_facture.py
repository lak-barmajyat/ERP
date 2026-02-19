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
        self.pushButton_2.setProperty("transparent", "true")  # Annuler
        self.pushButton_3.setProperty("transparent", "true")  # Supprimer
        self.pushButton_8.setProperty("transparent", "true")  # Supprimer
        
        # Connect buttons
        self.pushButton.clicked.connect(self.valider)
        self.pushButton_2.clicked.connect(self.button_2_clicked)
        self.pushButton_3.clicked.connect(self.button_3_clicked)
        self.pushButton_4.clicked.connect(self.button_4_clicked)
        
        # Connect combo boxes
        self.comboBox.currentIndexChanged.connect(self.client_changed)
        self.comboBox_2.currentIndexChanged.connect(self.article_changed)
        
        # Initialize table
        self.setup_table()
        
        # Load initial data
        self.load_clients()
        self.load_articles()
        
        # Load sample data into table
        self.load_sample_data()
    
    def setup_table(self):
        """Initialize the table widget"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)
    
    def load_clients(self):
        """Load clients into comboBox"""
        # TODO: Load from database
        self.comboBox.addItem("Client 1")
        self.comboBox.addItem("Client 2")
        self.comboBox.addItem("Client 3")
    
    def load_articles(self):
        """Load articles into comboBox_2"""
        # TODO: Load from database
        self.comboBox_2.addItem("Article 1")
        self.comboBox_2.addItem("Article 2")
        self.comboBox_2.addItem("Article 3")
    
    def client_changed(self, index):
        """Handle client selection change"""
        if index >= 0:
            client_name = self.comboBox.currentText()
            print(f"Client selected: {client_name}")
            # TODO: Load client details (ICE, etc.)
    
    def article_changed(self, index):
        """Handle article selection change"""
        if index >= 0:
            article_name = self.comboBox_2.currentText()
            print(f"Article selected: {article_name}")
            # TODO: Load article details
    
    def valider(self):
        """Handle Valider button click"""
        print("Valider clicked")
        # TODO: Validate and save facture
        client = self.comboBox.currentText()
        ice = self.lineEdit_3.text()
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        piece_num = self.lineEdit.text()
        
        print(f"Client: {client}, ICE: {ice}, Date: {date}, N° Piece: {piece_num}")
    
    def button_2_clicked(self):
        """Handle pushButton_2 click"""
        print("Button 2 clicked")
        # TODO: Implement functionality
    
    def button_3_clicked(self):
        """Handle pushButton_3 click"""
        print("Button 3 clicked")
        # TODO: Implement functionality
    
    def button_4_clicked(self):
        """Handle pushButton_4 click"""
        print("Button 4 clicked")
        # TODO: Implement functionality
    
    def add_row_to_table(self, ref, designation, puht, pttc, qte, taxe, total_ttc):
        """Add a row to the table"""
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(ref))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(designation))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(puht)))
        self.tableWidget.setItem(row_position, 3, QTableWidgetItem(str(pttc)))
        self.tableWidget.setItem(row_position, 4, QTableWidgetItem(str(qte)))
        self.tableWidget.setItem(row_position, 5, QTableWidgetItem(str(taxe)))
        self.tableWidget.setItem(row_position, 6, QTableWidgetItem(str(total_ttc)))
    
    def load_sample_data(self):
        """Load sample data into the table for testing"""
        # Sample data: (ref, designation, puht, pttc, qte, taxe, total_ttc)
        sample_data = [
            ("ART-001", "Ordinateur portable Dell XPS 15", 8500.00, 10200.00, 2, "20%", 20400.00),
            ("ART-002", "Clavier mécanique RGB", 450.00, 540.00, 5, "20%", 2700.00),
            ("ART-003", "Souris sans fil Logitech", 250.00, 300.00, 3, "20%", 900.00),
            ("ART-004", "Écran LED 27 pouces", 1800.00, 2160.00, 4, "20%", 8640.00),
            ("ART-005", "Casque audio Bluetooth", 650.00, 780.00, 2, "20%", 1560.00),
        ]
        
        for data in sample_data:
            self.add_row_to_table(*data)


def main():
    """Main function for testing the ClientsFacturesWindow"""
    app = QApplication(sys.argv)
    window = ClientsFacturesWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
