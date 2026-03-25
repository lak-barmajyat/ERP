import os
import sys

from PyQt5.QtWidgets import (
    QApplication,
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
from .select_doc_type import SelectDocTypeDialog
from .product_selector_widget import ProductSelectorWidget


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class NouveauDocWindow(QMainWindow):
    def __init__(self, parent=None):
        super(NouveauDocWindow, self).__init__(parent)
        loadUi(resource_path("doc_product_selector.ui"), self)

        # Keep this as a top-level owned window so parent lifetime controls it.
        self.setWindowFlag(Qt.Window, True)

        self._setup_table()
        self._setup_defaults()
        self._setup_icons()
        self._setup_product_selector_connections()

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

        self.doc_type_window = SelectDocTypeDialog()
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
        self.ttc_lineedit.setReadOnly(True)
        self.total_tax_label.setReadOnly(True)
        self.total_UT_label.setReadOnly(True)
        self.total_ttc_label.setReadOnly(True)

        # Read-only prices until a product is selected
        self.puht_editline.setReadOnly(True)
        self.pttc_editline.setReadOnly(True)

        # Lock entry fields until document is validated
        self._set_entry_fields_enabled(False)

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

        stmt = (
            select(
                Article.id_article,
                Article.reference_interne,
                Article.nom_article,
                Article.description,
                Article.prix_vente_ht,
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
        self.taxe_editline.setText(f'{float(product.get("tax", 0)):.2f}' if product.get("tax") is not None else "")
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

    @with_db_session
    def _setup_clients_lineedit(self, session=None):
        line_edit: QLineEdit = self.clients_lineedit
        original_stylesheet = line_edit.styleSheet()

        self._clients_autocomplete = LineEditAutoComplete(line_edit, self)

        if original_stylesheet:
            line_edit.setStyleSheet(original_stylesheet)

        stmt = (
            select(Tiers.nom_tiers)
            .where(Tiers.type_tiers == "CLIENT")
            .order_by(Tiers.nom_tiers)
        )

        names = session.execute(stmt).scalars().all()
        clients = [n for n in names if n]
        clients = self._normalize_client_names(clients)
        self._clients_autocomplete.set_items(clients)

        self.clients_lineedit.textChanged.connect(
            lambda: _on_client_name_text_changed(self.clients_lineedit.text())
        )
        self.clientid_lineedit.textChanged.connect(
            lambda: _on_client_id_text_changed(self.clientid_lineedit.text())
        )

        def _on_client_name_text_changed(lineedit_text):
            if self.clients_lineedit.hasFocus():
                if lineedit_text.strip() == "":
                    self.clientid_lineedit.clear()
                else:
                    stmt = (
                        select(Tiers.code_tiers)
                        .where(
                            and_(
                                Tiers.type_tiers == "CLIENT",
                                Tiers.nom_tiers.like(f"%{lineedit_text.strip()}%"),
                            )
                        )
                        .order_by(Tiers.nom_tiers)
                        .limit(1)
                    )

                    result = session.execute(stmt).scalar_one_or_none()
                    self.clientid_lineedit.setText(result if result else "")

        def _on_client_id_text_changed(id_input_text):
            if self.clientid_lineedit.hasFocus():
                if id_input_text.strip() == "":
                    self.clients_lineedit.clear()
                else:
                    stmt = (
                        select(Tiers.nom_tiers)
                        .where(
                            and_(
                                Tiers.type_tiers == "CLIENT",
                                Tiers.code_tiers.like(f"%{id_input_text.strip()}%"),
                            )
                        )
                        .order_by(Tiers.nom_tiers)
                        .limit(1)
                    )

                    result = session.execute(stmt).scalar_one_or_none()
                    self.clients_lineedit.setText(result if result else "")

    def current_selected_client(self) -> str:
        return self.clients_lineedit.text().strip()


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
