from __future__ import annotations
from program.services import (Tiers,
                            select,
                            delete,
                            update,
                            with_db_session,
                            generate_document_number,
                            insert,
                            Document,
                            Article,
                            DetailDocument,
                            and_,
                            RefTypeDocument)

from PyQt5.QtWidgets import (QDialog, QCompleter, QComboBox,
                             QMessageBox, QTableWidgetItem)
from PyQt5.QtCore import QStringListModel, Qt, QSortFilterProxyModel, QDate
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

@with_db_session
def _valider(self, session=None):
    id_tiers = session.execute(
        select(Tiers.id_tiers)
        .where(
            (Tiers.nom_tiers == self.clients_lineedit.text().strip()) &
            (Tiers.code_tiers == self.clientid_lineedit.text().strip()) &
            (Tiers.type_tiers == "CLIENT")
        )
    ).scalar_one_or_none()

    if not id_tiers:
        # Try to auto-fix: partial match on code first, then partial match on name
        code_input = self.clientid_lineedit.text().strip()
        name_input = self.clients_lineedit.text().strip()

        lookup_filter = None
        if code_input:
            lookup_filter = and_(Tiers.type_tiers == "CLIENT",
                                 Tiers.code_tiers.like(f"%{code_input}%"))
        elif name_input:
            lookup_filter = and_(Tiers.type_tiers == "CLIENT",
                                 Tiers.nom_tiers.like(f"%{name_input}%"))

        row = session.execute(
            select(Tiers.nom_tiers, Tiers.code_tiers)
            .where(lookup_filter)
            .order_by(Tiers.nom_tiers)
            .limit(1)
        ).one_or_none() if lookup_filter is not None else None

        if row:
            self.clients_lineedit.setText(row.nom_tiers)
            self.clientid_lineedit.setText(row.code_tiers)
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
            self.clientid_lineedit.clear()
            show_error_message("Client introuvable. Veuillez sélectionner un client valide.")
            return

    id_type_document = session.execute(
        select(RefTypeDocument.id_type_document)
        .where(RefTypeDocument.code_type == self.current_doc_type)
    ).scalar_one_or_none()

    if not id_type_document:
        show_error_message(f"Type de document '{self.current_doc_type}' introuvable.")
        return

    numero_document = self.ndocument_lineedit.text().strip()
    if not numero_document:
        numero_document = generate_document_number(self.current_doc_type)
        self.ndocument_lineedit.setText(numero_document)

    if not numero_document:
        show_error_message("Numéro de document invalide.")
        return

    document = Document(
        id_domaine=1,
        id_type_document=id_type_document,
        numero_document=numero_document,
        id_tiers=id_tiers,
        date_document=self.date_dateedit.date().toPyDate(),
        date_livraison=datetime.now().date(),
        mode_prix="HT",
        total_ht=0,
        total_tva=0,
        total_ttc=0,
        solde=0,
        id_vendeur=int(os.getenv("USER_ID", "6")),
        id_statut=1,
        commentaire=""
    )

    session.add(document)
    session.commit()


    self._clients_autocomplete.set_enabled(False)
    self.clientid_lineedit.setReadOnly(True)
    self.date_dateedit.setReadOnly(True)
    self.valider_button.setEnabled(False)

    # Unlock article entry fields and action buttons
    self._set_entry_fields_enabled(True)

    self.current_document_id = document.id_document

def _recalculate_entry(self):
    """Recalculate the per-line Total TTC preview field."""
    try:
        puht = float(self.puht_editline.text() or 0)
        qte = float(self.qte_lineedit.text() or 1)
        taxe_text = self.taxe_editline.text().replace("%", "")
        taxe = float(taxe_text) / 100
        pttc = puht * (1 + taxe)
        total = pttc * qte
        self.pttc_editline.setText(f"{pttc:.2f}")
        self.ttc_lineedit.setText(f"{total:.2f}")
    except ValueError:
        self.ttc_lineedit.setText("")

def _on_annuler(self):
    """Clear the article entry fields."""
    self.articles_combobox.clear()
    self.designation_editline.clear()
    self.puht_editline.clear()
    self.pttc_editline.clear()
    self.qte_lineedit.setText("1")
    self.ttc_lineedit.clear()
    self._editing_detail_id = None
    self.articles_combobox.setReadOnly(False)

@with_db_session
def _on_supprimer(self, session=None):
    """Remove the currently selected row from the table."""
    selected = self.tableWidget.selectedItems()
    # get id_article from the first column of the selected row
    if selected:
        id_detail_item = self.tableWidget.item(selected[0].row(), 7)  # Hidden ID Detail column
        if id_detail_item:
            id_detail = id_detail_item.text()
            session.execute(delete(DetailDocument).where(DetailDocument.id_detail == id_detail))
            session.commit()
            self.tableWidget.removeRow(selected[0].row())
            _recalculate_totals(self)
    _on_annuler(self)
        
@with_db_session
def _on_enregistrer(self, session=None):
    """Insert a new line or update the selected one."""
    if not self.current_document_id:
        show_error_message("Veuillez valider le document avant d'ajouter des lignes.")
        return

    ref_text = self.articles_combobox.text().strip()
    desig = self.designation_editline.text().strip()

    try:
        ref = ref_text
        puht = float(self.puht_editline.text() or 0)
        pttc = float(self.pttc_editline.text() or 0)
        qte = float(self.qte_lineedit.text() or 1)
        taxe = float(self.taxe_editline.text().replace("%", "") or 0)
        total = float(self.ttc_lineedit.text() or 0)
    except ValueError:
        show_error_message("Ligne invalide. Vérifiez la référence article, les prix, la quantité et la taxe.")
        return

    query = select(Article.id_article).where(Article.reference_interne == ref)
    id_article = session.execute(query).scalar_one_or_none()
    if not id_article:
        show_error_message(f"Article avec référence '{ref}' introuvable.")
        return

    editing_detail_id = getattr(self, "_editing_detail_id", None)
    if editing_detail_id:
        try:
            editing_detail_id = int(editing_detail_id)
        except ValueError:
            show_error_message("Ligne sélectionnée invalide. Veuillez resélectionner la ligne.")
            return

        query = (
            update(DetailDocument)
            .where(
                (DetailDocument.id_detail == editing_detail_id) &
                (DetailDocument.id_document == self.current_document_id)
            )
            .values(
                id_article=id_article,
                description=desig,
                prix_unitaire_ht=puht,
                prix_unitaire_ttc=pttc,
                quantite=qte,
                taux_tva=taxe,
                total_ligne_ttc=total,
            )
        )
    else:
        query = insert(DetailDocument).values(
            id_document=self.current_document_id,
            id_article=id_article,
            description=desig,
            prix_unitaire_ht=puht,
            prix_unitaire_ttc=pttc,
            quantite=qte,
            taux_tva=taxe,
            total_ligne_ttc=total
        )

    session.execute(query)
    session.commit()
    _reload_table(self)

@with_db_session
def _reload_table(self, session=None):
    self.tableWidget.setRowCount(0)  # Clear and reload to show the new line with its ID
    query = (
        select(DetailDocument)
        .where(DetailDocument.id_document == self.current_document_id)
        .order_by(DetailDocument.id_detail)
    )
    details = session.execute(query).scalars().all()


    for detail in details:
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        query = select(Article.reference_interne).where(Article.id_article == detail.id_article)
        ref = session.execute(query).scalar_one_or_none() or ""
        row_values = [
            ref,
            detail.description or "",
            detail.prix_unitaire_ht,
            detail.prix_unitaire_ttc,
            detail.quantite,
            detail.taux_tva,
            detail.total_ligne_ttc,
            detail.id_detail,
        ]
        for col, value in enumerate(row_values):
            item = QTableWidgetItem(str(value if value is not None else ""))
            item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if col not in (0, 1) else Qt.AlignLeft))
            self.tableWidget.setItem(row, col, item)

    _recalculate_totals(self)
    _on_annuler(self)  # clear entry fields after adding

def _on_nouveau(self):
    """Reset the entire document form."""
    self.tableWidget.setRowCount(0)
    _on_annuler(self)
    self.date_dateedit.setDate(QDate.currentDate())
    self.clientid_lineedit.clear()
    self.clients_lineedit.clear()
    self.taxe_editline.clear()
    self.total_tax_label.setText("0.00")
    self.total_UT_label.setText("0.00")
    self.total_ttc_label.setText("0.00")
    _update_table_stats(self)
    self._clients_autocomplete.set_enabled(True)  # Re-enable for next document
    self.clientid_lineedit.setReadOnly(False)
    self.date_dateedit.setReadOnly(False)
    self.valider_button.setEnabled(True)
    self._set_entry_fields_enabled(False)  # Lock article fields
    self.current_document_id = None

    # Always prepare a fresh document number (do not clear it)
    self.ndocument_lineedit.setText(generate_document_number(self.current_doc_type))
    self.ndocument_lineedit.setReadOnly(True)

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
    _update_table_stats(self)

def _update_table_stats(self):
    """Refresh small stats shown under the lines table."""
    if not hasattr(self, "tableWidget"):
        return

    rows_count = self.tableWidget.rowCount()
    selected_rows = len({item.row() for item in self.tableWidget.selectedItems()})

    if hasattr(self, "tableStatsRowsLabel"):
        self.tableStatsRowsLabel.setText(f"Rows: {rows_count}")
    if hasattr(self, "tableStatsSelectedLabel"):
        self.tableStatsSelectedLabel.setText(f"Selected: {selected_rows}")

def _on_table_row_selected(self):
    """Load selected table row values into entry fields for editing."""
    selected = self.tableWidget.selectedItems()
    if not selected:
        _update_table_stats(self)
        return

    row = selected[0].row()
    ref = (self.tableWidget.item(row, 0) or QTableWidgetItem("")).text()
    designation = (self.tableWidget.item(row, 1) or QTableWidgetItem("")).text()
    puht = (self.tableWidget.item(row, 2) or QTableWidgetItem("")).text()
    pttc = (self.tableWidget.item(row, 3) or QTableWidgetItem("")).text()
    qte = (self.tableWidget.item(row, 4) or QTableWidgetItem("1")).text()
    taxe = (self.tableWidget.item(row, 5) or QTableWidgetItem("")).text()
    total = (self.tableWidget.item(row, 6) or QTableWidgetItem("")).text()
    id_detail = (self.tableWidget.item(row, 7) or QTableWidgetItem("")).text().strip()

    self.articles_combobox.setText(ref)
    self.designation_editline.setText(designation)
    self.puht_editline.setText(puht)
    self.pttc_editline.setText(pttc)
    self.qte_lineedit.setText(qte)
    self.taxe_editline.setText(taxe)
    self.ttc_lineedit.setText(total)
    self._editing_detail_id = id_detail or None

    self.articles_combobox.setReadOnly(True)
    _update_table_stats(self)


@with_db_session
def _connect_signals(self, session=None):
    """Wire up button signals."""
    self.annule.clicked.connect(lambda: _on_annuler(self))
    self.suprimer.clicked.connect(lambda: _on_supprimer(self))
    self.enrgistrer.clicked.connect(lambda: _on_enregistrer(self))
    self.btn_fermer.clicked.connect(self.close)
    self.btn_nouveau.clicked.connect(lambda: _on_nouveau(self))
    self.tableWidget.itemSelectionChanged.connect(lambda: _on_table_row_selected(self))

    # Auto-calculate Total TTC entry field when inputs change
    self.puht_editline.textChanged.connect(lambda: _recalculate_entry(self))
    self.qte_lineedit.textChanged.connect(lambda: _recalculate_entry(self))
    self.taxe_editline.textChanged.connect(lambda: _recalculate_entry(self))

    # Article reference field is a QLineEdit in the UI.
    # Use editing signals so Enter and focus change (including Tab) refresh line data.
    if hasattr(self.articles_combobox, "returnPressed"):
        self.articles_combobox.returnPressed.connect(lambda: ref_tab_func(self))
    if hasattr(self.designation_editline, "returnPressed"):
        self.designation_editline.returnPressed.connect(lambda: _on_designation_return_pressed(self))
    if hasattr(self.articles_combobox, "editingFinished"):
        self.articles_combobox.editingFinished.connect(lambda: ref_tab_func(self))

    _update_table_stats(self)

@with_db_session
def _on_designation_return_pressed(self, session=None):
    """Resolve designation to an article reference and refresh linked fields."""
    designation_text = self.designation_editline.text().strip()
    if not designation_text:
        return

    # Prefer exact match; fallback to first partial match.
    article_ref = session.execute(
        select(Article.reference_interne)
        .where(Article.description == designation_text)
        .limit(1)
    ).scalar_one_or_none()

    if not article_ref:
        article_ref = session.execute(
            select(Article.reference_interne)
            .where(Article.description.like(f"%{designation_text}%"))
            .order_by(Article.id_article)
            .limit(1)
        ).scalar_one_or_none()

    if article_ref:
        self.articles_combobox.setText(article_ref)
        ref_tab_func(self)

@with_db_session
def ref_tab_func(self, session=None):
    """fill designation automatically when we select an article reference"""
    query = select(Article).where(Article.reference_interne == self.articles_combobox.text().strip())
    article = session.execute(query).scalar_one_or_none()

    self.designation_editline.setText(article.description if article else "")
    self.puht_editline.setText(f"{article.prix_vente_ht:.2f}" if article else "")
    self.taxe_editline.setText(f"{article.taux_tva:.2f}" if article else "")
    _recalculate_totals(self)
    _recalculate_entry(self)

def nouveau_doc_setup(self):
    result = self.doc_type_window.exec_()
    if result != QDialog.Accepted:
        return
    self.show()

    self.tableWidget.setColumnCount(8)  # Adjust column count to include the hidden ID column
    self.tableWidget.setHorizontalHeaderLabels(["Ref", "Désignation", "PU HT", "PU TTC", "Qte", "Taxe", "Total TTC", "ID Detail"])
    self.tableWidget.setColumnHidden(7, True)  # Hide the ID Detail column
    self.current_doc_type = self.doc_type_window.get_current_doc_type()
    self.setWindowTitle(f"Nouveau document - {self.current_doc_type}")
    self.ndocument_lineedit.setText(generate_document_number(self.current_doc_type))
    self.ndocument_lineedit.setReadOnly(False)

    self.valider_button.clicked.connect(lambda: _valider(self))
    self._editing_detail_id = None

    _connect_signals(self)

    # when focus on ref article combo and I press tab it should fill the designation and the price and the tax of the article and recalculate the total ttc of the line
    

    # you have to link database documents to their tables after creating them, so we load the articles for the new document (which will be empty)

    # and unlink id type tiers and link type tiers only

    # id_type_tiers will be the id to define the clients or the founissers by (CL001 , FR001)