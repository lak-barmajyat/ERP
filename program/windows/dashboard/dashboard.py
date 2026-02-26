from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap
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
        loadUi(resource_path("dash.ui"), self)

        self._did_apply_default_screen_geometry = False

        # Logo size (width x height in pixels)
        self.logo_config = {'icon_w': 170, 'icon_h': 50}

        # Footer icon sizes (user_icon and badge_icon in the footer bar)
        self.footer_icon_configs = {
            'footerUserIconLabel': {'icon': '../../assets/global/user_icon.svg',  'icon_w': 14, 'icon_h': 14},
            'footerRoleIconLabel': {'icon': '../../assets/global/badge_icon.svg', 'icon_w': 14, 'icon_h': 14},
        }

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

        # Initialize buttons with fixed sizes
        self._setup_buttons()
        self._setup_logo()
        self._setup_stat_icons()
        self._setup_footer_icons()

    def _apply_default_window_geometry_from_screen(self):
        """Maximize the window on the current screen (keeps title bar)."""
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return

        # Ensure the window is on the target screen before maximizing.
        available = screen.availableGeometry()
        if available.isValid():
            self.move(available.topLeft())

        # Use normal maximized state (not fullscreen) so the OS title bar
        # with close/minimize buttons remains visible.
        self.setWindowState(self.windowState() | Qt.WindowMaximized)

    def showEvent(self, event):
        super().showEvent(event)

        # Apply once: make the default window size fit the current PC screen.
        if not self._did_apply_default_screen_geometry:
            self._apply_default_window_geometry_from_screen()
            self._did_apply_default_screen_geometry = True

    def _setup_footer_icons(self):
        """Set pixmap and size for footer icon labels (user_icon and badge_icon)."""
        for label_name, config in self.footer_icon_configs.items():
            label = getattr(self, label_name, None)
            if label:
                w, h = config['icon_w'], config['icon_h']
                label.setFixedSize(QSize(w, h))
                label.setScaledContents(False)
                label.setAlignment(Qt.AlignCenter)
                pixmap = QPixmap(resource_path(config['icon'])).scaled(
                    w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                label.setPixmap(pixmap)

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

    def _setup_logo(self):
        """Resize the sidebar logo icon (logoIconLabel)."""
        label = getattr(self, 'logoIconLabel', None)
        if label:
            w = self.logo_config['icon_w']
            h = self.logo_config['icon_h']
            label.setFixedSize(QSize(w, h))

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
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()