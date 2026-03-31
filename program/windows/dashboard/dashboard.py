import os
import re
import sys
from datetime import datetime, timedelta

from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QDialog, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget,
                             QGraphicsDropShadowEffect)

from ..liste_ventes import SalesDocumentsWindow
from ..liste_achats import PurchaseDocumentsWindow
from ..liste_articles import ArticlesWindow
from ..liste_clients import ClientsWindow
from .dash_widget import DashboardWidget
from .historique_window import HistoriqueWindow
from program.services import Article, AuditLog, Document, LogoutDialog, MessageBox, Tiers, Utilisateur, func, select, with_db_session
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

        # Auto-refresh audit history (Historique) every 10 seconds.
        # Use `None` to load all available audit rows.
        self._audit_history_limit = None
        self._audit_refresh_timer = QTimer(self)
        self._audit_refresh_timer.setInterval(10_000)
        self._audit_refresh_timer.timeout.connect(self._refresh_audit_activity)

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

        self._audit_refresh_timer.start()
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

        # Clients page
        self.list_clients = ClientsWindow()
        self.contentStackedWidget.addWidget(self.list_clients)
        
        # Set dashboard widget as the default page (index 1, since mainScrollArea is index 0)
        self.contentStackedWidget.setCurrentIndex(1)
        
        # Connect dashboard widget buttons
        self.dashboard_widget.btn_liste_ventes_doc.clicked.connect(lambda: self._show_page(2))
        self.dashboard_widget.btn_liste_clients.clicked.connect(lambda: self._show_page(5))
        self.dashboard_widget.btn_liste_produits.clicked.connect(self._show_articles_page)

        self.dashboard_widget.btn_ajouter_client.clicked.connect(self._open_new_client_dialog)
        self.dashboard_widget.btn_ajouter_produit.clicked.connect(self._open_new_article_dialog)
        self.dashboard_widget.btn_fiche_client.clicked.connect(self._open_client_sheet_hint)

        self.dashboard_widget.btn_nouveau_pay.clicked.connect(lambda: self._not_implemented("Paiements"))
        self.dashboard_widget.btn_liste_pay.clicked.connect(lambda: self._not_implemented("Paiements"))

        self.dashboard_widget.btn_voir_historique.clicked.connect(
            self._open_full_historique_window
        )
        self._load_audit_activity(limit=self._audit_history_limit)
        self._refresh_dashboard_stats()

    def _open_full_historique_window(self) -> None:
        """Open the full Historique window (all audit rows + search)."""
        existing = getattr(self, "_historique_window", None)
        if existing is not None:
            try:
                existing.show()
                existing.raise_()
                existing.activateWindow()
                return
            except RuntimeError:
                self._historique_window = None

        window = HistoriqueWindow(parent=self)
        window.setAttribute(Qt.WA_DeleteOnClose, True)
        window.destroyed.connect(lambda _obj=None: setattr(self, "_historique_window", None))
        self._historique_window = window
        window.show()
        window.raise_()
        window.activateWindow()

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
        self.btn_clients.clicked.connect(lambda: self._show_page(5))
        self.btn_fournisseurs.clicked.connect(lambda: self._not_implemented("Fournisseurs"))
        self.btn_stock.clicked.connect(self._show_articles_page)
        self.btn_paiements.clicked.connect(lambda: self._not_implemented("Paiements"))
        self.btn_rapports.clicked.connect(lambda: self._not_implemented("Rapports"))
        self.btn_admin.clicked.connect(lambda: self._not_implemented("Administration"))
        
        # Apply icons and set initial state
        self._apply_sidebar_icons()
        self._update_sidebar_state(1)  # Dashboard is index 1

    def _show_page(self, index: int) -> None:
        """Switch to a specific page in the stacked widget."""
        self.contentStackedWidget.setCurrentIndex(index)
        self._update_sidebar_state(index)

        # Keep Historique up-to-date when returning to dashboard.
        if int(index) == 1:
            self._load_audit_activity(limit=self._audit_history_limit)
            self._refresh_dashboard_stats()

    def _refresh_audit_activity(self) -> None:
        """Refresh Historique periodically (every 10 seconds) when on dashboard."""
        try:
            if int(self.contentStackedWidget.currentIndex()) != 1:
                return
        except Exception:
            return

        self._load_audit_activity(limit=self._audit_history_limit)
        self._refresh_dashboard_stats()

    @with_db_session
    def _refresh_dashboard_stats(self, session=None) -> None:
        """Refresh the 3 KPI cards on the dashboard."""
        widget = getattr(self, "dashboard_widget", None)
        if widget is None:
            return

        label_new_clients = getattr(widget, "statValue1", None)
        label_sales_today = getattr(widget, "statValue2", None)
        label_low_stock = getattr(widget, "statValue3", None)

        if label_new_clients is None and label_sales_today is None and label_low_stock is None:
            return

        now = datetime.now()
        today = now.date()
        cutoff_dt = now - timedelta(days=30)

        if label_new_clients is not None:
            try:
                new_clients_count = session.execute(
                    select(func.count(Tiers.id_tiers)).where(
                        Tiers.type_tiers == "CLIENT",
                        Tiers.actif.is_(True),
                        Tiers.created_at >= cutoff_dt,
                    )
                ).scalar_one()
                label_new_clients.setText(str(int(new_clients_count or 0)))
            except Exception:
                label_new_clients.setText("—")

        if label_sales_today is not None:
            try:
                sales_domain_id = getattr(getattr(self, "list_ventes", None), "doc_domain_id", 1)
                sales_count = session.execute(
                    select(func.count(Document.id_document)).where(
                        Document.doc_actif.is_(True),
                        Document.id_domaine == int(sales_domain_id),
                        Document.date_document == today,
                    )
                ).scalar_one()
                label_sales_today.setText(str(int(sales_count or 0)))
            except Exception:
                label_sales_today.setText("—")

        if label_low_stock is not None:
            try:
                low_stock_count = session.execute(
                    select(func.count(Article.id_article)).where(
                        Article.actif.is_(True),
                        Article.quantite_min.isnot(None),
                        Article.quantite < Article.quantite_min,
                    )
                ).scalar_one()
                label_low_stock.setText(str(int(low_stock_count or 0)))
            except Exception:
                label_low_stock.setText("—")

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
            5: 4,  # Clients -> btn_clients
        }
        
        active_button_index = page_to_button.get(active_index, 0)
        
        for i, btn in enumerate(self._sidebar_buttons):
            btn.setChecked(i == active_button_index)
        self._update_icon_colors()

    def _not_implemented(self, feature_label: str) -> None:
        MessageBox(
            variant="info",
            title=feature_label,
            message=f"{feature_label} : fonctionnalité non implémentée pour le moment.",
            parent=self,
        ).exec_()

    def _open_client_sheet_hint(self) -> None:
        # There is no dedicated fiche client page yet; jump to the clients list
        # and focus the search entry.
        self._show_page(5)
        QTimer.singleShot(0, self._focus_clients_search)

    def _focus_clients_search(self) -> None:
        widget = getattr(self, "list_clients", None)
        if widget is None:
            return

        search = getattr(widget, "editSearch", None)
        if search is None:
            return

        try:
            search.setFocus()
            search.setCursorPosition(len(search.text() or ""))
        except RuntimeError:
            return

    def _open_new_client_dialog(self) -> None:
        self._show_page(5)
        if hasattr(self.list_clients, "tbNew"):
            self.list_clients.tbNew.click()

    def _open_new_article_dialog(self) -> None:
        current_index = self.contentStackedWidget.currentIndex()
        if not self._ensure_articles_page():
            self._update_sidebar_state(current_index)
            return
        self._show_page(4)
        if hasattr(self.list_articles, "tbNew"):
            self.list_articles.tbNew.click()

    @with_db_session
    def _load_audit_activity(self, limit: int | None = None, session=None) -> None:
        widget = getattr(self, "dashboard_widget", None)
        if widget is None:
            return

        list_widget = getattr(widget, "activityList", None)
        if list_widget is None:
            return

        today_label = getattr(widget, "activityTodayLabel", None)
        if today_label is not None:
            today_label.setText(datetime.now().strftime("%d/%m/%Y"))

        today = datetime.now().date()

        query = (
            select(
                AuditLog.date_action,
                AuditLog.id_utilisateur,
                AuditLog.action,
                AuditLog.table_name,
                AuditLog.record_id,
                AuditLog.commentaire,
                AuditLog.ip_client,
                AuditLog.old_values_json,
                AuditLog.new_values_json,
                Utilisateur.nom_utilisateur,
            )
            .outerjoin(Utilisateur, AuditLog.id_utilisateur == Utilisateur.id_utilisateur)
            .where(func.date(AuditLog.date_action) == today)
            # Sort by insertion order, not timestamps, so bad/future `date_action` values
            # cannot hide the newest events.
            .order_by(AuditLog.id_audit.desc())
        )

        if limit is not None:
            query = query.limit(int(limit))

        rows = session.execute(query).all()

        def _clean_comment(text: str) -> str:
            value = (text or "").strip()
            if not value:
                return ""

            # Normalize spaces and use a nicer multiplication sign.
            value = re.sub(r"\s+", " ", value)
            value = value.replace(" x ", " × ")

            # Improve common phrases (keep backward compatibility with existing rows).
            value = re.sub(r"^Création\s+document\s*:\s*", "Création du document ", value, flags=re.IGNORECASE)
            value = re.sub(r"^Suppression\s+document\s*:\s*", "Suppression du document ", value, flags=re.IGNORECASE)

            value = re.sub(r"^Ajout\s+ligne\s*\(", "Ajout d'une ligne (", value, flags=re.IGNORECASE)
            value = re.sub(r"^Modification\s+ligne\s*\(", "Modification d'une ligne (", value, flags=re.IGNORECASE)
            value = re.sub(r"^Suppression\s+ligne\s*\(", "Suppression d'une ligne (", value, flags=re.IGNORECASE)

            value = re.sub(r"^Création\s+client\s*:\s*", "Création du client ", value, flags=re.IGNORECASE)
            value = re.sub(r"^Modification\s+client\s*:\s*", "Modification du client ", value, flags=re.IGNORECASE)
            value = re.sub(r"^Désactivation\s+client\s*:\s*", "Désactivation du client ", value, flags=re.IGNORECASE)

            value = re.sub(r"^Création\s+article\s*:\s*", "Création de l'article ", value, flags=re.IGNORECASE)
            value = re.sub(r"^Modification\s+article\s*:\s*", "Modification de l'article ", value, flags=re.IGNORECASE)
            value = re.sub(r"^Désactivation\s+article\s*:\s*", "Désactivation de l'article ", value, flags=re.IGNORECASE)

            value = value.replace("detail#", "détail #")
            return value.strip()

        def _format_timestamp(value: datetime | None) -> str:
            if value is None:
                return ""
            try:
                return value.strftime("%H:%M")
            except Exception:
                return str(value)

        def _action_label(action: str | None) -> str:
            key = (action or "").strip().upper()
            return {
                "INSERT": "Création",
                "UPDATE": "Modification",
                "DELETE": "Suppression",
                "STATUS_CHANGE": "Changement de statut",
            }.get(key, key or "Action")

        def _element_label(table_name: str | None) -> str:
            key = (table_name or "").strip().lower()
            return {
                "documents": "document",
                "details_documents": "ligne de document",
                "tiers": "client",
                "articles": "article",
                "mouvements_stock": "mouvement de stock",
            }.get(key, key or "élément")

        def _source_label(table_name: str | None, ip_client: str | None) -> str:
            ip = (ip_client or "").strip()
            if ip:
                return ip

            key = (table_name or "").strip().lower()
            return {
                "documents": "Documents",
                "details_documents": "Documents",
                "tiers": "Clients",
                "articles": "Articles",
                "mouvements_stock": "Stock",
            }.get(key, (table_name or "").strip() or "Application")

        def _fmt_value(value) -> str:
            if value is None:
                return "—"
            if isinstance(value, bool):
                return "Oui" if value else "Non"
            if isinstance(value, (int, float)):
                try:
                    if float(value).is_integer():
                        return str(int(value))
                except Exception:
                    pass
                return str(value)

            text = str(value).strip()
            return text if text else "—"

        def _summarize_changes(action: str | None, old_values, new_values) -> str:
            old_dict = old_values if isinstance(old_values, dict) else {}
            new_dict = new_values if isinstance(new_values, dict) else {}

            action_key = (action or "").strip().upper()
            if not old_dict and not new_dict:
                return ""

            if action_key == "INSERT" and new_dict:
                pairs = [f"{k}={_fmt_value(new_dict.get(k))}" for k in sorted(new_dict.keys())]
            elif action_key == "DELETE" and old_dict:
                pairs = [f"{k}={_fmt_value(old_dict.get(k))}" for k in sorted(old_dict.keys())]
            else:
                keys = sorted(set(old_dict.keys()) | set(new_dict.keys()))
                pairs = []
                for k in keys:
                    before = old_dict.get(k)
                    after = new_dict.get(k)
                    if before == after:
                        continue
                    pairs.append(f"{k}: {_fmt_value(before)} → {_fmt_value(after)}")

            if not pairs:
                return ""

            max_pairs = 3
            shown = pairs[:max_pairs]
            extra = len(pairs) - len(shown)
            text = ", ".join(shown)
            if extra > 0:
                text = f"{text}, +{extra} champ(s)"
            return text

        def _fallback_description(action: str, table_name: str, record_id: str) -> str:
            action_value = (action or "").strip().upper()
            table_value = (table_name or "").strip().lower()
            rid = (record_id or "").strip()

            action_label = {
                "INSERT": "Création",
                "UPDATE": "Mise à jour",
                "DELETE": "Suppression",
                "STATUS_CHANGE": "Changement de statut",
            }.get(action_value, action_value or "Action")

            table_label = {
                "documents": "document",
                "details_documents": "ligne de document",
                "tiers": "client",
                "articles": "article",
            }.get(table_value, table_value or "élément")

            suffix = f" #{rid}" if rid else ""
            return f"{action_label} {table_label}{suffix}".strip()

        list_widget.blockSignals(True)
        try:
            list_widget.clear()
            for date_action, user_id, action, table_name, record_id, commentaire, ip_client, old_json, new_json, username in rows:
                who = (username or "").strip()
                if not who:
                    who = f"Utilisateur {int(user_id)}" if user_id is not None else "Système"

                ts = _format_timestamp(date_action)
                action_txt = _action_label(action)
                element_txt = _element_label(table_name)
                rid = (record_id or "").strip()
                element = f"{element_txt} #{rid}" if rid else element_txt
                source = _source_label(table_name, ip_client)

                comment = _clean_comment(commentaire or "")
                change = comment if comment else _summarize_changes(action, old_json, new_json)
                if not change:
                    change = "—"

                list_widget.addItem(f"{who} | {ts} | {action_txt} sur {element} depuis {source} : {change}")
        finally:
            list_widget.blockSignals(False)

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