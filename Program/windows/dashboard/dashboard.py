from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import os


def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super(DashboardWindow, self).__init__()
        loadUi(resource_path("dashboard.ui"), self)

        self.ajouter_client.setIcon(QIcon(resource_path("../../assets/dashboard/ajouter_client.svg")))
        self.ajouter_client.setIconSize(QSize(70, 70))
        self.ajouter_client.setText("Ajoute Client")
        self.ajouter_client.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.liste_clients.setIcon(QIcon(resource_path("../../assets/dashboard/liste_clients.svg")))
        self.liste_clients.setIconSize(QSize(70, 70))
        self.liste_clients.setText("Liste Clients")
        self.liste_clients.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.fiche_client.setIcon(QIcon(resource_path("../../assets/dashboard/fiche_client.svg")))
        self.fiche_client.setIconSize(QSize(70, 70))
        self.fiche_client.setText("Fiche Client")
        self.fiche_client.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.nouvau_doc.setIcon(QIcon(resource_path("../../assets/dashboard/nouveau_doc.svg")))
        self.nouvau_doc.setIconSize(QSize(47, 70))
        self.nouvau_doc.setText("Nouveau Doc")
        self.nouvau_doc.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.liste_ventes.setIcon(QIcon(resource_path("../../assets/dashboard/liste_ventes.svg")))
        self.liste_ventes.setIconSize(QSize(70, 70))
        self.liste_ventes.setText("Liste Ventes")
        self.liste_ventes.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.ajouter_produit.setIcon(QIcon(resource_path("../../assets/dashboard/ajouter_produit.svg")))
        self.ajouter_produit.setIconSize(QSize(58, 70))
        self.ajouter_produit.setText("Ajoute Produit")
        self.ajouter_produit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.liste_produits.setIcon(QIcon(resource_path("../../assets/dashboard/liste_produits.svg")))
        self.liste_produits.setIconSize(QSize(70, 70))
        self.liste_produits.setText("Liste Produits")
        self.liste_produits.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.ajouter_stock.setIcon(QIcon(resource_path("../../assets/dashboard/ajouter_stock.svg")))
        self.ajouter_stock.setIconSize(QSize(60, 70))
        self.ajouter_stock.setText("Ajouter Stock")
        self.ajouter_stock.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.nouveau_pay.setIcon(QIcon(resource_path("../../assets/dashboard/nouveau_pay.svg")))
        self.nouveau_pay.setIconSize(QSize(80, 70))
        self.nouveau_pay.setText("Nouveau Pay")
        self.nouveau_pay.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.liste_pay.setIcon(QIcon(resource_path("../../assets/dashboard/liste_pay.svg")))
        self.liste_pay.setIconSize(QSize(75, 70))
        self.liste_pay.setText("Liste Pay")
        self.liste_pay.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)


def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()