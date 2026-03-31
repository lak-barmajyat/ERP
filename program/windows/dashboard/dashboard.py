import os
import sys

from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import QSize, Qt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QDialog, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget,
                             QGraphicsDropShadowEffect)

from ..liste_ventes import SalesDocumentsWindow
from ..liste_achats import PurchaseDocumentsWindow
from ..liste_articles import ArticlesWindow
from .dash_widget import DashboardWidget
from program.services import LogoutDialog, MessageBox
from program.themes.shared_input_popup_style import apply_global_font_to_window

# Icon configuration constants
ICON_SIZE = 20
ICON_COLOR_SELECTED = "#1d7ae2"  # Blue for active
ICON_COLOR_UNSELECTED = "#6b7280"  # Gray for inactive

ICON_PATHS = {
    'btn_dashboard': '../../assets/global/nav_dashboard.svg',
    'btn_ventes': '../../assets/global/nav_ventes.svg',
    'btn_achats': '../../assets/global/nav_achats.svg',
    'btn_produits': '../../assets/global/nav_produits.svg',
    'btn_clients': '../../assets/global/nav_clients.svg',
    'btn_fournisseurs': '../../assets/global/nav_fournisseurs.svg',
    'btn_stock': '../../assets/global/nav_stock.svg',
    'btn_paiements': '../../assets/global/nav_paiements.svg',
    'btn_rapports': '../../assets/global/nav_rapports.svg',
    'btn_admin': '../../assets/global/nav_admin.svg',
}


def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_colored_icon(icon_path: str, color_name: str) -> QIcon:
    """Return a QIcon with all opaque pixels recolored to *color_name*."""
    full_path = resource_path(icon_path)
    pixmap = QPixmap(full_path)
    if pixmap.isNull():
        return QIcon()
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color_name))
    painter.end()
    return QIcon(pixmap)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super(DashboardWindow, self).__init__()
        loadUi(resource_path("dashboard.ui"), self)
        apply_global_font_to_window(self)

        self._did_apply_default_screen_geometry = False

        # Logo size (width x height in pixels)
        self.logo_config = {'icon_w': 170, 'icon_h': 50}

        # Footer icon sizes (user_icon and badge_icon in the footer bar)
        self.footer_icon_configs = {
            'footerUserIconLabel': {'icon': '../../assets/global/user_icon.svg',  'icon_w': 14, 'icon_h': 14},
            'footerRoleIconLabel': {'icon': '../../assets/global/badge_icon.svg', 'icon_w': 14, 'icon_h': 14},
        }

        # Initialize buttons with fixed sizes
        self._setup_logo()
        self._setup_footer_icons()
        self._setup_stacked_widget()
        self._wire_sidebar()
        self.btn_logout.clicked.connect(self.show_logout_dialog)
        self.showMaximized()

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

    def _setup_logo(self):
        """Resize the sidebar logo icon (logoIconLabel)."""
        label = getattr(self, 'logoIconLabel', None)
        if label:
            w = self.logo_config['icon_w']
            h = self.logo_config['icon_h']
            label.setFixedSize(QSize(w, h))

    def _setup_stacked_widget(self):
        """Set default page and connect navigation buttons"""
        # Create dashboard widget instance and add it to stacked widget
        self.dashboard_widget = DashboardWidget()
        self.contentStackedWidget.addWidget(self.dashboard_widget)
        
        # Create liste ventes widget and add to stacked widget
        self.list_ventes = SalesDocumentsWindow()
        self.contentStackedWidget.addWidget(self.list_ventes)

        # Create liste achats widget and add to stacked widget
        self.list_achats = PurchaseDocumentsWindow()
        self.contentStackedWidget.addWidget(self.list_achats)

        # Reserve the Articles page slot (lazy instantiate on click).
        # This prevents the whole dashboard from crashing if the DB schema
        # hasn't been migrated yet (e.g. missing articles.quantite columns).
        self._articles_placeholder = QWidget()
        self.list_articles = None
        self.contentStackedWidget.addWidget(self._articles_placeholder)
        
        # Set dashboard widget as the default page (index 1, since mainScrollArea is index 0)
        self.contentStackedWidget.setCurrentIndex(1)
        
        # Connect dashboard widget buttons
        self.dashboard_widget.btn_liste_ventes_doc.clicked.connect(lambda: self._show_page(2))

    def _wire_sidebar(self) -> None:
        """Wire sidebar navigation buttons to pages and manage their states."""
        self._sidebar_buttons: list[QPushButton] = [
            self.btn_dashboard,
            self.btn_ventes,
            self.btn_achats,
            self.btn_produits,
            self.btn_clients,
            self.btn_fournisseurs,
            self.btn_stock,
            self.btn_paiements,
            self.btn_rapports,
            self.btn_admin,
        ]
        
        # Connect buttons to pages
        self.btn_dashboard.clicked.connect(lambda: self._show_page(1))
        self.btn_ventes.clicked.connect(lambda: self._show_page(2))
        self.btn_achats.clicked.connect(lambda: self._show_page(3))
        self.btn_produits.clicked.connect(self._show_articles_page)
        # Add more connections as needed for other buttons
        
        # Apply icons and set initial state
        self._apply_sidebar_icons()
        self._update_sidebar_state(1)  # Dashboard is index 1

    def _show_page(self, index: int) -> None:
        """Switch to a specific page in the stacked widget."""
        self.contentStackedWidget.setCurrentIndex(index)
        self._update_sidebar_state(index)

    def _show_articles_page(self) -> None:
        """Open Articles page (create it the first time)."""
        current_index = self.contentStackedWidget.currentIndex()
        if not self._ensure_articles_page():
            self._update_sidebar_state(current_index)
            return
        self._show_page(4)

    def _ensure_articles_page(self) -> bool:
        """Ensure the Articles page widget exists in the stack."""
        if getattr(self, "list_articles", None) is not None:
            return True

        placeholder = getattr(self, "_articles_placeholder", None)
        if placeholder is None:
            return False

        try:
            widget = ArticlesWindow()
        except Exception as exc:
            details = str(exc) if exc is not None else ""
            message = "Impossible de charger la liste des articles."
            if "Unknown column" in details:
                message = (
                    "Impossible de charger la liste des articles.\n\n"
                    "La base de données n'est pas à jour (colonnes articles.quantite / quantite_min / quantite_max)."
                )

            MessageBox(
                variant="attention",
                title="Articles",
                message=message,
                parent=self,
            ).exec_()
            return False

        idx = self.contentStackedWidget.indexOf(placeholder)
        if idx < 0:
            idx = 4

        self.contentStackedWidget.removeWidget(placeholder)
        placeholder.deleteLater()
        self.contentStackedWidget.insertWidget(idx, widget)

        self._articles_placeholder = None
        self.list_articles = widget
        return True

    def _update_sidebar_state(self, active_index: int) -> None:
        """Update sidebar button states based on active page."""
        # Map page index to button index
        page_to_button = {
            1: 0,  # Dashboard -> btn_dashboard
            2: 1,  # Liste ventes -> btn_ventes
            3: 2,  # Liste achats -> btn_achats
            4: 3,  # Articles -> btn_produits
        }
        
        active_button_index = page_to_button.get(active_index, 0)
        
        for i, btn in enumerate(self._sidebar_buttons):
            btn.setChecked(i == active_button_index)
        self._update_icon_colors()

    def _apply_sidebar_icons(self) -> None:
        """Attach icons from assets/ to sidebar buttons using get_colored_icon."""
        size = QSize(ICON_SIZE, ICON_SIZE)
        for btn in self._sidebar_buttons:
            btn.setIconSize(size)
            btn.setCheckable(True)
        self._update_icon_colors()

    def _update_icon_colors(self) -> None:
        """Set icon color per button: selected = darker, unselected = muted."""
        for btn in self._sidebar_buttons:
            btn_name = btn.objectName()
            if btn_name in ICON_PATHS:
                path = ICON_PATHS[btn_name]
                color = ICON_COLOR_SELECTED if btn.isChecked() else ICON_COLOR_UNSELECTED
                btn.setIcon(get_colored_icon(path, color))
    
    def show_logout_dialog(self):
        from program.windows.login import LoginWindow
        dialog = LogoutDialog(self)
        result = dialog.exec_()

        if result == 1:  # Déconnexion
            self.close()
            self.login_window = LoginWindow()
            self.login_window.show()

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()