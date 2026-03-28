import sys
import os
from dataclasses import dataclass

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QHeaderView, QWidget, QAbstractItemView
from PyQt5.QtCore import Qt, QDate
from PyQt5.uic import loadUi

from .funcs import liste_ventes_setup


@dataclass(frozen=True)
class DocumentsContext:
    domain_id: int
    domain_code: str
    domain_label: str
    tiers_type: str
    tiers_label: str
    tiers_code_prefix: str
    article_price_field: str


SALES_CONTEXT = DocumentsContext(
    domain_id=1,
    domain_code="VENTE",
    domain_label="Ventes",
    tiers_type="CLIENT",
    tiers_label="Client",
    tiers_code_prefix="CL",
    article_price_field="prix_vente_ht",
)


PURCHASE_CONTEXT = DocumentsContext(
    domain_id=2,
    domain_code="ACHAT",
    domain_label="Achats",
    tiers_type="FOURNISSEUR",
    tiers_label="Fournisseur",
    tiers_code_prefix="FR",
    article_price_field="prix_achat_ht",
)


def resource_path(relative_path: str) -> str:
    """
    Resolve a resource path relative to this file.

    This works both in normal development and when the
    application is bundled with tools like PyInstaller.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class SalesDocumentsWindow(QWidget):
    """
    Main window controller for the sales documents list (liste_ventes.ui).
    """

    def __init__(self, context: DocumentsContext | None = None) -> None:
        super().__init__()
        self.context = context or SALES_CONTEXT
        loadUi(resource_path("liste_ventes.ui"), self)

        self.doc_domain_id = self.context.domain_id
        self.doc_domain_code = self.context.domain_code
        self.doc_domain_label = self.context.domain_label
        self.tiers_type_filter = self.context.tiers_type
        self.article_price_field = self.context.article_price_field

        self._apply_context_to_ui()
        self._setup_table()
        self._setup_defaults()
        liste_ventes_setup(self)

    def _apply_context_to_ui(self) -> None:
        """Update labels/placeholders to match sales vs purchases context."""
        if hasattr(self, "labelClient"):
            self.labelClient.setText(self.context.tiers_label)
        if hasattr(self, "labelcodeclient"):
            self.labelcodeclient.setText(f"Code {self.context.tiers_label}")
        if hasattr(self, "editClient"):
            self.editClient.setPlaceholderText(f"Rechercher un {self.context.tiers_label.lower()}...")
        if hasattr(self, "editcodeclient"):
            self.editcodeclient.setPlaceholderText(f"ex: {self.context.tiers_code_prefix}00122")

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #

    def _setup_table(self) -> None:
        """
        Configure the documents table (column widths, behavior, etc.).
        """
        header = self.tableDocuments.horizontalHeader()
        header.setStretchLastSection(False)
        
        # Set all columns to resize to content except Client column
        # Column 4: Client - takes remaining space        
        for i in range(8):
            if i == 4:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # Hide row headers for a cleaner, grid-like look
        self.tableDocuments.verticalHeader().setVisible(False)
        self.tableDocuments.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableDocuments.setSortingEnabled(True)

    def _setup_defaults(self) -> None:
        """
        Set default values for the filters and summary section.
        """
        today = QDate.currentDate()
        self.dateFrom.setDate(today.addYears(-10))
        self.dateTo.setDate(today)

        self.comboStatus.setCurrentIndex(0)  # "Tous les statuts"

        self.labelNbDocumentsValue.setText("0")
        self.labelTotalHtValue.setText("0,00 €")
        self.labelTotalTtcValue.setText("0,00 €")
        self.labelTotalBalanceValue.setText("0,00 €")

    def _connect_signals(self) -> None:
        """
        Legacy local wiring kept for backward compatibility.
        Runtime signal wiring is handled by `liste_ventes_setup` in funcs.py.
        """
        return

    def _populate_demo_data(self) -> None:
        """
        Optional demo data so the UI looks similar to the HTML mockup.
        You can remove or replace this with real data loading logic.
        """
        rows = [
            ("Facture", "FAC-2023-001089", "12/10/2023", "TechSolutions SARL",
             "4 500,00 €", "5 400,00 €", "0,00 €", "Payé"),
            ("Devis", "DEV-2023-00452", "11/10/2023", "Consulting & Co.",
             "1 200,00 €", "1 440,00 €", "-", "Brouillon"),
            ("Facture", "FAC-2023-001088", "10/10/2023", "Alpha Industries",
             "8 950,50 €", "10 740,60 €", "10 740,60 €", "Impayé"),
        ]

        self.tableDocuments.setRowCount(0)

        for data in rows:
            row = self.tableDocuments.rowCount()
            self.tableDocuments.insertRow(row)

            # Checkbox column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.tableDocuments.setItem(row, 0, checkbox_item)

            # Other columns
            for col, value in enumerate(data, start=1):
                item = QTableWidgetItem(value)
                # Align numeric columns to the right
                if col in (5, 6, 7):
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                else:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.tableDocuments.setItem(row, col, item)

        self._recalculate_summary()

    # ------------------------------------------------------------------ #
    # Actions / Slots
    # ------------------------------------------------------------------ #

    def _on_filter_clicked(self) -> None:
        """
        Placeholder for filter logic.
        Currently just recomputes the summary values.
        """
        self._recalculate_summary()

    def _on_new_document(self) -> None:
        """
        Placeholder for opening a 'new document' window.
        """
        # Integrate with your NouveauDocWindow or other logic here.
        pass

    def _on_edit_document(self) -> None:
        """
        Placeholder for editing the currently selected document.
        """
        pass

    def _on_delete_document(self) -> None:
        """
        Legacy placeholder disabled.
        Deletion is handled in funcs.py with DB soft-delete (`doc_actif = 0`).
        """
        return

    def _on_print_documents(self) -> None:
        """
        Placeholder for printing logic.
        """
        pass

    def _on_export_excel(self) -> None:
        """
        Placeholder for exporting the table to Excel.
        """
        pass

    # ------------------------------------------------------------------ #
    # Data helpers
    # ------------------------------------------------------------------ #

    def _recalculate_summary(self) -> None:
        """
        Recalculate basic totals from the table values.
        This mimics the footer figures in the HTML mockup.
        """
        nb_docs = self.tableDocuments.rowCount()
        total_ht = 0.0
        total_ttc = 0.0
        balance = 0.0

        for row in range(nb_docs):
            ht_text = (self.tableDocuments.item(row, 5) or QTableWidgetItem("0")).text()
            ttc_text = (self.tableDocuments.item(row, 6) or QTableWidgetItem("0")).text()
            solde_text = (self.tableDocuments.item(row, 7) or QTableWidgetItem("0")).text()

            ht_val = self._parse_amount(ht_text)
            ttc_val = self._parse_amount(ttc_text)
            solde_val = self._parse_amount(solde_text)

            total_ht += ht_val
            total_ttc += ttc_val
            balance += solde_val

        self.labelNbDocumentsValue.setText(str(nb_docs))
        self.labelTotalHtValue.setText(self._format_amount(total_ht))
        self.labelTotalTtcValue.setText(self._format_amount(total_ttc))
        self.labelTotalBalanceValue.setText(self._format_amount(balance))

    @staticmethod
    def _parse_amount(text: str) -> float:
        """
        Convert an amount like '4 500,00 €' to a float.
        """
        cleaned = (
            text.replace("€", "")
            .replace(" ", "")
            .replace("\xa0", "")
            .replace(",", ".")
            .strip()
        )
        if cleaned in ("", "-"):
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _format_amount(value: float) -> str:
        """
        Format a float back to a French-style monetary string.
        """
        # Format as 2 decimals then swap '.' and ',' and insert spaces
        s = f"{value:,.2f}"
        s = s.replace(",", " ").replace(".", ",")
        return f"{s} €"


def main() -> None:
    """
    Standalone launcher for testing the SalesDocumentsWindow.
    """
    app = QApplication(sys.argv)
    window = SalesDocumentsWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

