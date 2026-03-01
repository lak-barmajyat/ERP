import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt
from PyQt5.uic import loadUi


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class DashboardWidget(QWidget):
    """Dashboard content widget (stats, buttons, activity)"""
    
    def __init__(self):
        super(DashboardWidget, self).__init__()
        loadUi(resource_path("dash_widget.ui"), self)
        
        # Stat icon sizes:
        #   container_size — diameter of the colored circle background (px)
        #   icon_w / icon_h — inner SVG icon size (should be smaller than container for padding)
        self.stat_icon_configs = {
            'statIcon1': {'icon': '../../assets/dashboard/stat_clients.svg', 'container_size': 48, 'icon_w': 26, 'icon_h': 26},
            'statIcon2': {'icon': '../../assets/dashboard/stat_ventes.svg',  'container_size': 48, 'icon_w': 26, 'icon_h': 26},
            'statIcon3': {'icon': '../../assets/dashboard/stat_stock.svg',   'container_size': 48, 'icon_w': 26, 'icon_h': 26},
        }

        # Store button configurations
        self.button_configs = {
            'btn_ajouter_client':   {'icon': '../../assets/dashboard/ajouter_client.svg',  'text': '  Ajouter Client',   'icon_w': 70, 'icon_h': 60},
            'btn_liste_clients':    {'icon': '../../assets/dashboard/liste_clients.svg',   'text': '  Liste Clients',    'icon_w': 70, 'icon_h': 40},
            'btn_fiche_client':     {'icon': '../../assets/dashboard/fiche_client.svg',    'text': '  Fiche Client',     'icon_w': 65, 'icon_h': 40},
            'btn_nouveau_doc':      {'icon': '../../assets/dashboard/nouveau_doc.svg',     'text': '  Nouveau Doc',      'icon_w': 45, 'icon_h': 70},
            'btn_liste_ventes_doc': {'icon': '../../assets/dashboard/liste_ventes.svg',    'text': '  Liste Ventes',     'icon_w': 65, 'icon_h': 60},
            'btn_ajouter_produit':  {'icon': '../../assets/dashboard/ajouter_produit.svg', 'text': '  Ajouter Produit',  'icon_w': 60, 'icon_h': 40},
            'btn_liste_produits':   {'icon': '../../assets/dashboard/liste_produits.svg',  'text': '  Liste Produits',   'icon_w': 60, 'icon_h': 50},
            'btn_nouveau_pay':      {'icon': '../../assets/dashboard/nouveau_pay.svg',     'text': '  Nouveau Pay',      'icon_w': 65, 'icon_h': 45},
            'btn_liste_pay':        {'icon': '../../assets/dashboard/liste_pay.svg',       'text': '  Liste Paiements',  'icon_w': 65, 'icon_h': 45},
        }
        
        # Initialize widgets
        self._setup_stat_icons()
        self._setup_buttons()
    
    def _setup_stat_icons(self):
        """Configure stat icon labels: fix container size, center the inner SVG with padding."""
        for label_name, config in self.stat_icon_configs.items():
            label = getattr(self, label_name, None)
            if label:
                cs = config['container_size']
                # Fix the label (circle background) to the container size
                label.setFixedSize(QSize(cs, cs))
                # Disable stretch so the pixmap sits centered with padding
                label.setScaledContents(False)
                label.setAlignment(Qt.AlignCenter)
                # Scale SVG to the inner icon size (smaller = more padding inside circle)
                pixmap = QPixmap(resource_path(config['icon'])).scaled(
                    config['icon_w'], config['icon_h'],
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                label.setPixmap(pixmap)
    
    def _setup_buttons(self):
        """Setup all tool buttons with icons and text"""
        for button_name, config in self.button_configs.items():
            button = getattr(self, button_name, None)
            if button:
                button.setIcon(QIcon(resource_path(config['icon'])))
                button.setIconSize(QSize(config['icon_w'], config['icon_h']))
                button.setText(config['text'])
                button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)


def main():
    """Standalone launcher for testing the DashboardWidget"""
    app = QApplication(sys.argv)
    widget = DashboardWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
