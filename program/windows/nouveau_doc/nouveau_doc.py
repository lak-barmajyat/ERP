import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt, QDate
from PyQt5.uic import loadUi
import os


import os
import sys

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QLineEdit

from program.services import generate_document_number, with_db_session, select, Tiers
from program.widgetstyles.lineedit_combo_style import LineEditAutoComplete
from .select_doc_type import SelectDocTypeDialog

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class NouveauDocWindow(QMainWindow):
    def __init__(self):
        super(NouveauDocWindow, self).__init__()
        loadUi(resource_path("doc.ui"), self)

        self._setup_table()
        self._setup_defaults()
        self._connect_signals()

    def _setup_table(self):
        """Configure the document lines table."""
        header = self.docTable.horizontalHeader()
        # Stretch Designation column, fix the rest
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)   # Designation expands

        self.docTable.setColumnWidth(0, 150)   # Reference Article
        self.docTable.setColumnWidth(2, 100)   # P.U.H.T
        self.docTable.setColumnWidth(3, 100)   # P.T.T.C
        self.docTable.setColumnWidth(4, 70)    # Qte
        self.docTable.setColumnWidth(5, 80)    # Taxe
        self.docTable.setColumnWidth(6, 110)   # Totale TTC

        self.docTable.verticalHeader().setVisible(False)
        self.docTable.setRowCount(0)

        self.doc_type_window = SelectDocTypeDialog()
        self.selected_doc_type = self.doc_type_window.get_selected_doc_type()
        self.setWindowTitle(f"Nouveau document - {self.selected_doc_type}")
        self.n_piece_editline.setText(generate_document_number(self.selected_doc_type))
        self.n_piece_editline.setReadOnly(True)
        self.n_piece_editline.setStyleSheet("color: gray;")

        # Clients LineEdit with autocomplete
        self._setup_clients_lineedit()

    def _setup_defaults(self):
        """Set sensible default values for form fields."""
        self.dateInput.setDate(QDate.currentDate())
        self.qteInput.setText("1")
        self.totalTtcEntryInput.setReadOnly(True)
        self.totalTaxValue.setReadOnly(True)
        self.totalUTValue.setReadOnly(True)
        self.totalTTCValue.setReadOnly(True)

    def _connect_signals(self):
        """Wire up button signals."""
        self.btn_annuler.clicked.connect(self._on_annuler)
        self.btn_supprimer.clicked.connect(self._on_supprimer)
        self.btn_enregistrer.clicked.connect(self._on_enregistrer)
        self.btn_fermer.clicked.connect(self.close)
        self.btn_nouveau.clicked.connect(self._on_nouveau)

        # Auto-calculate Total TTC entry field when inputs change
        self.puhtInput.textChanged.connect(self._recalculate_entry)
        self.qteInput.textChanged.connect(self._recalculate_entry)
        self.taxeInput.textChanged.connect(self._recalculate_entry)

    # ── Entry-row helpers ────────────────────────────────────────────────────

    def _recalculate_entry(self):
        """Recalculate the per-line Total TTC preview field."""
        try:
            puht = float(self.puhtInput.text() or 0)
            qte = float(self.qteInput.text() or 1)
            taxe_text = self.taxeInput.text().replace("%", "")
            taxe = float(taxe_text) / 100
            pttc = puht * (1 + taxe)
            total = pttc * qte
            self.pttcInput.setText(f"{pttc:.2f}")
            self.totalTtcEntryInput.setText(f"{total:.2f}")
        except ValueError:
            self.totalTtcEntryInput.setText("")

    def _on_annuler(self):
        """Clear the article entry fields."""
        self.refInput.clear()
        self.desigInput.clear()
        self.puhtInput.clear()
        self.pttcInput.clear()
        self.qteInput.setText("1")
        self.totalTtcEntryInput.clear()

    def _on_supprimer(self):
        """Remove the currently selected row from the table."""
        selected = self.docTable.selectedItems()
        if selected:
            row = self.docTable.currentRow()
            self.docTable.removeRow(row)
            self._recalculate_totals()

    def _on_enregistrer(self):
        """Add the current entry row to the document table."""
        ref = self.refInput.text()
        desig = self.desigInput.text()
        puht = self.puhtInput.text()
        pttc = self.pttcInput.text()
        qte = self.qteInput.text()
        taxe = self.taxeInput.text()
        total = self.totalTtcEntryInput.text()

        row = self.docTable.rowCount()
        self.docTable.insertRow(row)
        for col, value in enumerate([ref, desig, puht, pttc, qte, taxe, total]):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if col not in (0, 1) else Qt.AlignLeft))
            self.docTable.setItem(row, col, item)

        self._recalculate_totals()
        self._on_annuler()  # clear entry fields after adding

    def _on_nouveau(self):
        """Reset the entire document form."""
        self.docTable.setRowCount(0)
        self._on_annuler()
        self.dateInput.setDate(QDate.currentDate())
        self.pieceInput.clear()
        self.clientidinput.clear()
        self.clientinput.clear()
        self.totalTaxValue.setText("0.00")
        self.totalUTValue.setText("0.00")
        self.totalTTCValue.setText("0.00")

    def _recalculate_totals(self):
        """Recompute footer totals from the table rows."""
        total_ht = 0.0
        total_tax = 0.0
        total_ttc = 0.0
        for row in range(self.docTable.rowCount()):
            try:
                puht = float((self.docTable.item(row, 2) or QTableWidgetItem("0")).text() or 0)
                qte = float((self.docTable.item(row, 4) or QTableWidgetItem("1")).text() or 1)
                taxe_text = (self.docTable.item(row, 5) or QTableWidgetItem("0%")).text().replace("%", "")
                taxe = float(taxe_text) / 100
                ht = puht * qte
                tax = ht * taxe
                total_ht += ht
                total_tax += tax
                total_ttc += ht + tax
            except ValueError:
                continue
        self.totalUTValue.setText(f"{total_ht:.2f}")
        self.totalTaxValue.setText(f"{total_tax:.2f}")
        self.totalTTCValue.setText(f"{total_ttc:.2f}")
    
    @with_db_session
    def _setup_clients_lineedit(self, session=None):
        line_edit: QLineEdit = self.clients_lineedit
        self._clients_autocomplete = LineEditAutoComplete(line_edit, self)

        query = (
            select(Tiers.nom_tiers)
            .where(Tiers.type_tiers == "CLIENT")
            .order_by(Tiers.nom_tiers)
        )
        # scalars() => list[str]
        names = session.execute(query).scalars().all()
        clients = [n for n in names if n]
        clients = self._normalize_client_names(clients)
        self._clients_autocomplete.set_items(clients)

        
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

        

    def current_selected_client(self) -> str:
        return self.clients_lineedit.text().strip()


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

