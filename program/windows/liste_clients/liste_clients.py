import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from program.themes.shared_input_popup_style import apply_global_font_to_window

class ListeClientsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ListeClientsWindow, self).__init__()
        
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "liste_clients.ui")
        uic.loadUi(ui_path, self)
        apply_global_font_to_window(self)
        
        # We can populate the table with some dummy data to match the screenshot
        self.populate_dummy_data()
        
        # Ensure the table expands properly
        header = self.tableClients.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # Checkbox column
        
    def populate_dummy_data(self):
        self.tableClients.setRowCount(2)
        
        # Row 1
        item_check = QtWidgets.QTableWidgetItem()
        item_check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item_check.setCheckState(Qt.Checked)
        self.tableClients.setItem(0, 0, item_check)
        self.tableClients.setItem(0, 1, QtWidgets.QTableWidgetItem("CLT-04291"))
        self.tableClients.setItem(0, 2, QtWidgets.QTableWidgetItem("Atlas Technologies SARL"))
        self.tableClients.setItem(0, 3, QtWidgets.QTableWidgetItem("001524873000091"))
        self.tableClients.setItem(0, 4, QtWidgets.QTableWidgetItem("+212 522-458900"))
        self.tableClients.setItem(0, 5, QtWidgets.QTableWidgetItem("contact@atlastech.ma"))
        self.tableClients.setItem(0, 6, QtWidgets.QTableWidgetItem("Casablanca"))
        self.tableClients.setItem(0, 7, QtWidgets.QTableWidgetItem("150 000,00"))
        self.tableClients.setItem(0, 8, QtWidgets.QTableWidgetItem("42 350,50"))
        self.tableClients.setItem(0, 9, QtWidgets.QTableWidgetItem("ACTIF"))
        
        # Row 2
        item_check2 = QtWidgets.QTableWidgetItem()
        item_check2.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item_check2.setCheckState(Qt.Unchecked)
        self.tableClients.setItem(1, 0, item_check2)
        self.tableClients.setItem(1, 1, QtWidgets.QTableWidgetItem("CLT-04292"))
        self.tableClients.setItem(1, 2, QtWidgets.QTableWidgetItem("M. Yassine Bennani"))
        self.tableClients.setItem(1, 3, QtWidgets.QTableWidgetItem("--"))
        self.tableClients.setItem(1, 4, QtWidgets.QTableWidgetItem("+212 661-123456"))
        self.tableClients.setItem(1, 5, QtWidgets.QTableWidgetItem("y.bennani@gmail.com"))
        self.tableClients.setItem(1, 6, QtWidgets.QTableWidgetItem("Rabat"))
        self.tableClients.setItem(1, 7, QtWidgets.QTableWidgetItem("10 000,00"))
        self.tableClients.setItem(1, 8, QtWidgets.QTableWidgetItem("0,00"))
        self.tableClients.setItem(1, 9, QtWidgets.QTableWidgetItem("ACTIF"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = ListeClientsWindow()
    window.show()
    
    # Just close automatically after 1 second if in automated test mode
    if os.environ.get("AUTO_TEST") == "1":
        QtCore.QTimer.singleShot(1000, app.quit)
        
    sys.exit(app.exec_())
