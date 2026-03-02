from __future__ import annotations
from program.services import (Tiers,
                            select,
                            with_db_session,
                            generate_document_number,
                            insert,
                            Document,
                            Article,
                            DetailDocument,
                            and_,
                            RefTypeDocument)
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QStringListModel, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QPalette, QColor
from datetime import datetime
import os


def show_error_message(message_text=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)  # أيقونة الخطأ الحمراء
    msg.setWindowTitle("Erreur")
    msg.setText(message_text)
    msg.setInformativeText("Veuillez vérifier les informations et réessayer.")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def create_document(data: dict, *, session):
    stmt = insert(Document).values(
        id_domaine=data["id_domaine"],
        id_type_document=data["id_type_document"],
        numero_document=data["numero_document"],
        id_tiers=data.get("id_tiers"),
        date_document=data["date_document"],
        date_livraison=data.get("date_livraison"),
        mode_prix=data.get("mode_prix", "HT"),
        total_ht=data.get("total_ht", 0),
        total_tva=data.get("total_tva", 0),
        total_ttc=data.get("total_ttc", 0),
        solde=data.get("solde", 0),
        id_vendeur=data["id_vendeur"],
        id_statut=data["id_statut"],
        commentaire=data.get("commentaire"),
    )

    result = session.execute(stmt)

    inserted_id = result.inserted_primary_key[0]
    return inserted_id

@with_db_session
def _valider(self, session=None):
    id_tiers = session.execute(
        select(Tiers.id_tiers)
        .where(
            (Tiers.nom_tiers == self.clients_lineedit.text().strip()) &
            (Tiers.code_tiers == self.clientidinput.text().strip()) &
            (Tiers.type_tiers == "CLIENT")
        )
    ).scalar_one_or_none()

    if not id_tiers:
        # Try to auto-fix by looking up the client by code only
        row = session.execute(
            select(Tiers.nom_tiers, Tiers.code_tiers)
            .where(and_(Tiers.type_tiers == "CLIENT",
                        Tiers.code_tiers == self.clientidinput.text().strip()))
            .order_by(Tiers.nom_tiers)
            .limit(1)
        ).one_or_none()

        if row:
            self.clients_lineedit.setText(row.nom_tiers)
            self.clientidinput.setText(row.code_tiers)
            # Re-fetch id_tiers with the corrected values
            id_tiers = session.execute(
                select(Tiers.id_tiers)
                .where(
                    (Tiers.nom_tiers == row.nom_tiers) &
                    (Tiers.code_tiers == row.code_tiers) &
                    (Tiers.type_tiers == "CLIENT")
                )
            ).scalar_one_or_none()
        else:
            self.clients_lineedit.clear()
            self.clientidinput.clear()
            show_error_message("Client introuvable. Veuillez sélectionner un client valide.")
            return

    id_type_document = session.execute(
        select(RefTypeDocument.id_type_document)
        .where(RefTypeDocument.code_type == self.selected_doc_type)
    ).scalar_one_or_none()

    if not id_type_document:
        show_error_message(f"Type de document '{self.selected_doc_type}' introuvable.")
        return

    document = Document(
        id_domaine=1,
        id_type_document=id_type_document,
        numero_document=self.n_piece_editline.text().strip(),
        id_tiers=id_tiers,
        date_document=self.dateEdit.date().toPyDate(),
        date_livraison=datetime.now().date(),
        mode_prix="HT",
        total_ht=0,
        total_tva=0,
        total_ttc=0,
        solde=0,
        id_vendeur=os.getenv('USER_ID', 6),  # default to 6 if not set
        id_statut=1,
        commentaire=""
        )

    session.add(document)
    session.commit()

    self._clients_autocomplete.set_enabled(False)
    self.clientidinput.setReadOnly(True)
    self.dateEdit.setReadOnly(True)
    self.btn_valider.setEnabled(False)

    self.current_document_id = document.id_document

def _connect_signals(self):
    """Wire up button signals."""
    self.annule.clicked.connect(self._on_annuler)
    self.suprimer.clicked.connect(self._on_supprimer)
    self.enrgistrer.clicked.connect(self._on_enregistrer)
    self.btn_fermer.clicked.connect(self.close)
    self.btn_nouveau.clicked.connect(self._on_nouveau)
    self.btn_fermer.clicked.connect(self.close)
    self.btn_nouveau.clicked.connect(self._on_nouveau)

    # Auto-calculate Total TTC entry field when inputs change
    self.puht_editline.textChanged.connect(self._recalculate_entry)
    self.qte_editline.textChanged.connect(self._recalculate_entry)
    self.taxe_editline.textChanged.connect(self._recalculate_entry)


def _recalculate_entry(self):
    """Recalculate the per-line Total TTC preview field."""
    try:
        puht = float(self.puht_editline.text() or 0)
        qte = float(self.qte_editline.text() or 1)
        taxe_text = self.taxe_editline.text().replace("%", "")
        taxe = float(taxe_text) / 100
        pttc = puht * (1 + taxe)
        total = pttc * qte
        self.pttc_editline.setText(f"{pttc:.2f}")
        self.total_ttc_editline.setText(f"{total:.2f}")
    except ValueError:
        self.total_ttc_editline.setText("")

def _on_annuler(self):
    """Clear the article entry fields."""
    self.articles_combobox.clear()
    self.designation_editline.clear()
    self.puht_editline.clear()
    self.pttc_editline.clear()
    self.qte_editline.setText("1")
    self.total_ttc_editline.clear()

def _on_supprimer(self):
    """Remove the currently selected row from the table."""
    selected = self.tableWidget.selectedItems()
    if selected:
        row = self.tableWidget.currentRow()
        self.tableWidget.removeRow(row)
        self._recalculate_totals()

def _on_enregistrer(self):
    """Add the current entry row to the document table."""
    ref = self.articles_combobox.text()
    desig = self.designation_editline.text()
    puht = self.puht_editline.text()
    pttc = self.pttc_editline.text()
    qte = self.qte_editline.text()
    taxe = self.taxe_editline.text()
    total = self.total_ttc_editline.text()

    row = self.tableWidget.rowCount()
    self.tableWidget.insertRow(row)
    for col, value in enumerate([ref, desig, puht, pttc, qte, taxe, total]):
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if col not in (0, 1) else Qt.AlignLeft))
        self.tableWidget.setItem(row, col, item)

    self._recalculate_totals()
    self._on_annuler()  # clear entry fields after adding

def _on_nouveau(self):
    """Reset the entire document form."""
    self.tableWidget.setRowCount(0)
    self._on_annuler()
    self.dateEdit.setDate(QDate.currentDate())
    self.n_piece_editline.clear()
    self.clients_lineedit.clear()
    self.clients_lineedit.clear()
    self.total_tax_label.setText("0.00")
    self.total_UT_label.setText("0.00")
    self.total_ttc_label.setText("0.00")

def _recalculate_totals(self):
    """Recompute footer totals from the table rows."""
    total_ht = 0.0
    total_tax = 0.0
    total_ttc = 0.0
    for row in range(self.tableWidget.rowCount()):
        try:
            puht = float((self.tableWidget.item(row, 2) or QTableWidgetItem("0")).text() or 0)
            qte = float((self.tableWidget.item(row, 4) or QTableWidgetItem("1")).text() or 1)
            taxe_text = (self.tableWidget.item(row, 5) or QTableWidgetItem("0%")).text().replace("%", "")
            taxe = float(taxe_text) / 100
            ht = puht * qte
            tax = ht * taxe
            total_ht += ht
            total_tax += tax
            total_ttc += ht + tax
        except ValueError:
            continue
    self.total_UT_label.setText(f"{total_ht:.2f}")
    self.total_tax_label.setText(f"{total_tax:.2f}")
    self.total_ttc_label.setText(f"{total_ttc:.2f}")

def _connect_signals(self):
    """Wire up button signals."""
    self.annule.clicked.connect(lambda: _on_annuler())
    self.suprimer.clicked.connect(lambda: _on_supprimer())
    self.enrgistrer.clicked.connect(lambda: _on_enregistrer())
    self.btn_fermer.clicked.connect(self.close)
    self.btn_nouveau.clicked.connect(lambda: _on_nouveau())

    # Auto-calculate Total TTC entry field when inputs change
    self.puht_editline.textChanged.connect(lambda: _recalculate_entry())
    self.qte_editline.textChanged.connect(lambda: _recalculate_entry())
    self.taxe_editline.textChanged.connect(lambda: _recalculate_entry())


def nouveau_doc_setup(self):
    result = self.doc_type_window.exec_()
    if result != QDialog.Accepted:
        return
    self.show()

    self.selected_doc_type = self.doc_type_window.get_selected_doc_type()
    self.setWindowTitle(f"Nouveau document - {self.selected_doc_type}")
    self.n_piece_editline.setText(generate_document_number(self.selected_doc_type))
    self.n_piece_editline.setReadOnly(True)

    self.btn_valider.clicked.connect(lambda: _valider(self))

    _connect_signals(self)


    # you have to link database documents to their tables after creating them, so we load the articles for the new document (which will be empty)

    # and unlink id type tiers and link type tiers only

    # id_type_tiers will be the id to define the clients or the founissers by (CL001 , FR001)