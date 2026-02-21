from PyQt5.QtGui import QGuiApplication, QIcon
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

        self._did_apply_default_screen_geometry = False

        # Store button configurations
        self.button_configs = {
            'ajouter_client': {'icon': "../../assets/dashboard/ajouter_client.svg", 'text': "Ajoute Client", 'size': 70},
            'liste_clients': {'icon': "../../assets/dashboard/liste_clients.svg", 'text': "Liste Clients", 'size': 70},
            'fiche_client': {'icon': "../../assets/dashboard/fiche_client.svg", 'text': "Fiche Client", 'size': 70},
            'nouvau_doc': {'icon': "../../assets/dashboard/nouveau_doc.svg", 'text': "Nouveau Doc", 'size': 70},
            'liste_ventes': {'icon': "../../assets/dashboard/liste_ventes.svg", 'text': "Liste Ventes", 'size': 70},
            'ajouter_produit': {'icon': "../../assets/dashboard/ajouter_produit.svg", 'text': "Ajoute Produit", 'size': 70},
            'liste_produits': {'icon': "../../assets/dashboard/liste_produits.svg", 'text': "Liste Produits", 'size': 70},
            'ajouter_stock': {'icon': "../../assets/dashboard/ajouter_stock.svg", 'text': "Ajouter Stock", 'size': 70},
            'nouveau_pay': {'icon': "../../assets/dashboard/nouveau_pay.svg", 'text': "Nouveau Pay", 'size': 80},
            'liste_pay': {'icon': "../../assets/dashboard/liste_pay.svg", 'text': "Liste Pay", 'size': 75}
        }

        # Configure scroll area functionality
        self._setup_scroll_area()
        
        # Initialize buttons with fixed sizes
        self._setup_buttons()

    def _setup_scroll_area(self):
        """Configure the scroll area defined in the UI file"""
        # The scroll area is already defined in the UI file
        # Here we just configure its behavior
        
        # Set the scroll area as central widget
        self.setCentralWidget(self.scrollArea)
        
        # Configure scroll bar policies (already set in UI, but can be modified here if needed)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # When the window is larger than the fixed content, center it.
        self.scrollArea.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        # Ensure the content widget has fixed size
        #self.scrollAreaWidgetContents.setMinimumSize(1920, 1080)
        #self.scrollAreaWidgetContents.setMaximumSize(1920, 1080)
        
        # Set widget resizable to False for fixed size content
        self.scrollArea.setWidgetResizable(False)
        
        # Set minimum window size
        self.setMinimumSize(640, 480)

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

    def _setup_buttons(self):
        """Setup all tool buttons with icons and text"""
        for button_name, config in self.button_configs.items():
            button = getattr(self, button_name, None)
            if button:
                button.setIcon(QIcon(resource_path(config['icon'])))
                button.setIconSize(QSize(config['size'], config['size']))
                button.setText(config['text'])
                button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)


def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()