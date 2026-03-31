import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHeaderView,
    QLineEdit,
    QMainWindow,
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.uic import loadUi

from program.services import (
    generate_document_number,
    with_db_session,
    select,
    Tiers,
    Article,
    and_,
    get_colored_icon,
    LineEditAutoComplete,
)
from program.themes.shared_input_popup_style import apply_input_styles_to_window
from .select_doc_type import SelectDocTypeDialog
from .product_selector_widget import ProductSelectorWidget


NOUVEAU_DOC_STYLE_MAP = {
    "__window__": ["QWidget", "global_font"],
    "__all_lineedits__": ["QLineEdit", "entry"],
    "__all_comboboxes__": ["QComboBox", "combobox"],
    "__all_dateedits__": ["QDateEdit", "dateedit"],
    "__all_combobox_popups__": ["QComboBox", "popup_list", {"row_height": 36}],
    "__all_completer_popups__": ["QLineEdit", "completer_popup", {"row_height": 36}],
    "btn_imprimer": ["QToolButton", "primary"],
    "btn_nouveau": ["QToolButton", "primary"],
    "enrgistrer": ["QPushButton", "primary"],
    "valider_button": ["QPushButton", "primary"],
    "btn_fermer": ["QPushButton", "secondary"],
    "annule": ["QPushButton", "secondary"],
}


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class NouveauDocWindow(QMainWindow):
    def __init__(
        self,
        parent=None,
        *,
        doc_domain_id: int = 1,
        tiers_type_filter: str = "CLIENT",
        article_price_field: str = "prix_vente_ht",
        tiers_label: str | None = None,
    ):
        super(NouveauDocWindow, self).__init__(parent)
        loadUi(resource_path("doc_product_selector.ui"), self)

        # Keep this as a top-level owned window so parent lifetime controls it.
        self.setWindowFlag(Qt.Window, True)

        self.doc_domain_id = int(doc_domain_id or 1)
        self.tiers_type_filter = (tiers_type_filter or "CLIENT").strip() or "CLIENT"
        self.article_price_field = (article_price_field or "prix_vente_ht").strip() or "prix_vente_ht"
        self.tiers_label = (tiers_label or self._default_tiers_label()).strip() or self._default_tiers_label()

        self._tiers_name_code_pairs: list[tuple[str, str]] = []
        self._apply_context_to_ui()

        self._setup_table()
        self._setup_taxe_combobox()
        self._setup_defaults()
        self._setup_icons()
        self._setup_product_selector_connections()
        self._setup_input_styles()

    def _default_tiers_label(self) -> str:
        return "Fournisseur" if str(self.tiers_type_filter).upper() == "FOURNISSEUR" else "Client"

    def apply_document_context(self, domain_id: int) -> None:
        """Apply sales/purchase context (labels + tiers type + article price field)."""
        domain_id = int(domain_id or 1)
        if domain_id == 2:
            self.doc_domain_id = 2
            self.tiers_type_filter = "FOURNISSEUR"
            self.article_price_field = "prix_achat_ht"
            self.tiers_label = "Fournisseur"
        else:
            self.doc_domain_id = 1
            self.tiers_type_filter = "CLIENT"
            self.article_price_field = "prix_vente_ht"
            self.tiers_label = "Client"

        self._apply_context_to_ui()
        self._reload_tiers_autocomplete_items()
        self._setup_product_selector()

    def _apply_context_to_ui(self) -> None:
        """Update Client/Fournisseur labels and placeholders to match context."""
        label = getattr(self, "clientLabel", None)
        if label is not None:
            label.setText((self.tiers_label or "").upper())

        id_label = getattr(self, "clientidLabel", None)
        if id_label is not None:
            id_label.setText(f"{self.tiers_label} id")

        name_edit = getattr(self, "clients_lineedit", None)
        if name_edit is not None and hasattr(name_edit, "setPlaceholderText"):
            name_edit.setPlaceholderText(self.tiers_label)

        code_edit = getattr(self, "clientid_lineedit", None)
        if code_edit is not None and hasattr(code_edit, "setPlaceholderText"):
            code_edit.setPlaceholderText(f"{self.tiers_label} ID")

    def _setup_input_styles(self):
        apply_input_styles_to_window(self, row_height=36, widget_styles_map=NOUVEAU_DOC_STYLE_MAP)

    def _setup_table(self):
        """Configure the document lines table."""
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)   # Designation expands

        self.tableWidget.setColumnWidth(0, 150)   # Reference Article
        self.tableWidget.setColumnWidth(2, 100)   # P.U.H.T
        self.tableWidget.setColumnWidth(3, 100)   # P.T.T.C
        self.tableWidget.setColumnWidth(4, 70)    # Qte
        self.tableWidget.setColumnWidth(5, 80)    # Taxe
        self.tableWidget.setColumnWidth(6, 110)   # Totale TTC

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setRowCount(0)

        self.doc_type_window = SelectDocTypeDialog(domain_id=self.doc_domain_id)
        self.selected_doc_type = self.doc_type_window.get_current_doc_type()
        self.setWindowTitle(f"Nouveau document - {self.selected_doc_type}")
        self.ndocument_lineedit.setText(generate_document_number(self.selected_doc_type))
        self.ndocument_lineedit.setReadOnly(True)

        self._setup_clients_lineedit()
        self._setup_product_selector()

    def _setup_defaults(self):
        """Set sensible default values for form fields."""
        self.date_dateedit.setDate(QDate.currentDate())
        self.qte_lineedit.setText("1")
        if hasattr(self, "taxe_editline") and hasattr(self.taxe_editline, "setCurrentText"):
            self.taxe_editline.setCurrentText("20.00%")
        self.ttc_lineedit.setReadOnly(True)
        self.total_tax_label.setReadOnly(True)
        self.total_UT_label.setReadOnly(True)
        self.total_ttc_label.setReadOnly(True)

        # Price remains editable once line fields are enabled.
        self.puht_editline.setReadOnly(False)
        self.pttc_editline.setReadOnly(True)

        # Lock entry fields until document is validated
        self._set_entry_fields_enabled(False)

    def _setup_taxe_combobox(self) -> None:
        """Replace taxe line edit with fixed tax combo options."""
        tax_widget = getattr(self, "taxe_editline", None)
        if isinstance(tax_widget, QComboBox):
            tax_widget.clear()
            tax_widget.addItems(["20.00%", "10.00%", "5.00%"])
            tax_widget.setCurrentText("20.00%")
            return

        if not isinstance(tax_widget, QLineEdit):
            return

        parent = tax_widget.parentWidget()
        tax_combo = QComboBox(parent)
        tax_combo.setObjectName("taxe_editline")
        tax_combo.setMinimumSize(tax_widget.minimumSize())
        tax_combo.setMaximumSize(tax_widget.maximumSize())
        tax_combo.setSizePolicy(tax_widget.sizePolicy())
        tax_combo.setFont(tax_widget.font())
        tax_combo.setEnabled(tax_widget.isEnabled())
        tax_combo.addItems(["20.00%", "10.00%", "5.00%"])
        tax_combo.setCurrentText("20.00%")

        parent_layout = parent.layout() if parent else None
        if parent_layout is not None:
            parent_layout.replaceWidget(tax_widget, tax_combo)
        else:
            tax_combo.setGeometry(tax_widget.geometry())

        tax_widget.hide()
        tax_widget.deleteLater()
        self.taxe_editline = tax_combo

    def _set_entry_fields_enabled(self, enabled: bool) -> None:
        """Enable or disable all article entry fields and their action buttons."""
        entry_widgets = [
            getattr(self, "productSelector", None),
            getattr(self, "puht_editline", None),
            getattr(self, "pttc_editline", None),
            getattr(self, "qte_lineedit", None),
            getattr(self, "taxe_editline", None),
        ]

        for w in entry_widgets:
            if w:
                w.setEnabled(enabled)

        for btn_name in ("annule", "enrgistrer", "suprimer"):
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setEnabled(enabled)

    def _setup_icons(self):
        """Apply colored icons to buttons."""
        self.btn_imprimer.setIcon(get_colored_icon('../../assets/global/print.svg', '#ffffff'))
        self.btn_imprimer.setIconSize(QSize(16, 16))

        self.btn_nouveau.setIcon(get_colored_icon('../../assets/global/add.svg', '#ffffff'))
        self.btn_nouveau.setIconSize(QSize(80, 80))

    # ── Product selector helpers ─────────────────────────────────────────────

    def _setup_product_selector_connections(self):
        if hasattr(self, "productSelector") and isinstance(self.productSelector, ProductSelectorWidget):
            self.productSelector.productSelected.connect(self._on_product_selected)

    @with_db_session
    def _setup_product_selector(self, session=None):
        """تحميل articles داخل ProductSelectorWidget."""
        if not hasattr(self, "productSelector"):
            return

        price_col = getattr(Article, self.article_price_field, Article.prix_vente_ht)

        stmt = (
            select(
                Article.id_article,
                Article.reference_interne,
                Article.nom_article,
                Article.description,
                price_col,
                Article.taux_tva,
            )
            .order_by(Article.id_article)
        )

        rows = session.execute(stmt).all()
        products = []

        for row in rows:
            article_id = row[0]
            reference_interne = row[1] or ""
            nom_article = row[2] or ""
            description = row[3] or ""
            prix_ht = float(row[4] or 0)
            taux_tva = float(row[5] or 0)

            full_description = nom_article
            if description and description.strip():
                full_description = f"{nom_article} - {description}"

            prix_ttc = prix_ht * (1 + taux_tva / 100.0)

            products.append({
                "id": article_id,
                "code": reference_interne,
                "description": full_description,
                "price": prix_ht,
                "price_ttc": prix_ttc,
                "tax": taux_tva,
            })

        self.productSelector.set_products(products)
        self.productSelector.set_popup_span_widget(self.puht_editline)





    def _on_product_selected(self, product):
        self.puht_editline.setText(f'{float(product.get("price", 0)):.2f}')
        self.pttc_editline.setText(f'{float(product.get("price_ttc", 0)):.2f}')
        if hasattr(self.taxe_editline, "setCurrentText"):
            self.taxe_editline.setCurrentText(f'{float(product.get("tax", 20.0)):.2f}%')
        if not self.qte_lineedit.text().strip():
            self.qte_lineedit.setText("1")

    # ── Clients helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _normalize_client_names(client_names):
        unique_names = []
        seen = set()

        for raw_name in client_names:
            if raw_name is None:
                continue

            normalized_name = str(raw_name).strip()
            if not normalized_name:
                continue

            key = normalized_name.casefold()
            if key in seen:
                continue

            seen.add(key)
            unique_names.append(normalized_name)

        unique_names.sort(key=str.casefold)
        return unique_names

    def _setup_clients_lineedit(self) -> None:
        """Setup tiers autocomplete and sync Name <-> Code fields.

        Important: avoid capturing DB sessions in callbacks; sessions are short-lived
        due to the `with_db_session` decorator.
        """
        line_edit: QLineEdit = self.clients_lineedit

        self._clients_autocomplete = LineEditAutoComplete(line_edit, self)
        self._reload_tiers_autocomplete_items()

        try:
            self.clients_lineedit.textChanged.disconnect(self._on_tiers_name_text_changed)
        except TypeError:
            pass
        self.clients_lineedit.textChanged.connect(self._on_tiers_name_text_changed)

        try:
            self.clientid_lineedit.textChanged.disconnect(self._on_tiers_code_text_changed)
        except TypeError:
            pass
        self.clientid_lineedit.textChanged.connect(self._on_tiers_code_text_changed)

    @with_db_session
    def _reload_tiers_autocomplete_items(self, session=None) -> None:
        tiers_type = (getattr(self, "tiers_type_filter", None) or "CLIENT").strip() or "CLIENT"

        rows = session.execute(
            select(Tiers.nom_tiers, Tiers.code_tiers)
            .where(Tiers.type_tiers == tiers_type)
            .order_by(Tiers.nom_tiers)
        ).all()

        pairs: list[tuple[str, str]] = []
        for name, code in rows:
            name = (name or "").strip()
            code = (code or "").strip()
            if not name:
                continue
            pairs.append((name, code))

        self._tiers_name_code_pairs = pairs
        names = self._normalize_client_names([name for name, _code in pairs])
        if hasattr(self, "_clients_autocomplete") and self._clients_autocomplete is not None:
            self._clients_autocomplete.set_items(names)

    def _find_first_code_for_name_fragment(self, fragment: str) -> str:
        q = (fragment or "").strip().casefold()
        if not q:
            return ""
        for name, code in getattr(self, "_tiers_name_code_pairs", []) or []:
            if q in name.casefold():
                return code or ""
        return ""

    def _find_first_name_for_code_fragment(self, fragment: str) -> str:
        q = (fragment or "").strip().casefold()
        if not q:
            return ""
        for name, code in getattr(self, "_tiers_name_code_pairs", []) or []:
            if q in (code or "").casefold():
                return name or ""
        return ""

    def _on_tiers_name_text_changed(self, text: str) -> None:
        if not getattr(self, "clients_lineedit", None) or not getattr(self, "clientid_lineedit", None):
            return

        if not self.clients_lineedit.hasFocus():
            return

        if (text or "").strip() == "":
            self.clientid_lineedit.clear()
            return

        code = self._find_first_code_for_name_fragment(text)
        self.clientid_lineedit.setText(code)

    def _on_tiers_code_text_changed(self, text: str) -> None:
        if not getattr(self, "clients_lineedit", None) or not getattr(self, "clientid_lineedit", None):
            return

        if not self.clientid_lineedit.hasFocus():
            return

        if (text or "").strip() == "":
            self.clients_lineedit.clear()
            return

        name = self._find_first_name_for_code_fragment(text)
        self.clients_lineedit.setText(name)

    def current_selected_client(self) -> str:
        return self.clients_lineedit.text().strip()


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
