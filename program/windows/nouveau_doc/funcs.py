
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
                            RefTypeDocument,
                            RefStatutDocument,
                            MessageBox,
                            log_audit_event)
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QTableWidgetItem,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QDate

from datetime import datetime
import os


class _NumericSortTableWidgetItem(QTableWidgetItem):
    """Sort numeric columns by hidden numeric value while preserving display text."""

    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            left = self.data(Qt.UserRole)
            right = other.data(Qt.UserRole)
            if left is not None and right is not None:
                return float(left) < float(right)
        return super().__lt__(other)


def _safe_float(value_text):
    text = str(value_text or "").strip().replace(" ", "")
    if text in ("", "-"):
        return 0.0

    # Support both "6,857.25" and "6857,25" formats.
    if "," in text and "." in text:
        text = text.replace(",", "")
    elif "," in text:
        if text.count(",") == 1 and len(text.split(",", 1)[1]) <= 2:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")

    try:
        return float(text)
    except ValueError:
        return 0.0


def _format_amount(value):
    """Format monetary values as #,###.##."""
    return f"{_safe_float(value):,.2f}"


def _format_qty(value):
    """Format quantity as integer with thousands separators and no decimals."""
    qty = int(round(_safe_float(value)))
    return f"{qty:,d}"


def _build_detail_item(value, align_right=False, numeric=False, quantity=False):
    """Create a row item that keeps display text but sorts numeric values correctly."""
    if numeric:
        display_text = _format_qty(value) if quantity else _format_amount(value)
        item = _NumericSortTableWidgetItem(display_text)
        item.setData(Qt.UserRole, _safe_float(value))
    else:
        display_text = str(value if value is not None else "")
        item = QTableWidgetItem(display_text)

    item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if align_right else Qt.AlignLeft))
    return item


def _status_label_key(label):
    return (label or "").strip().casefold().replace("é", "e").replace("è", "e").replace("ê", "e")


TAX_OPTIONS = ("20.00%", "10.00%", "5.00%")


def _tax_widget(self):
    return getattr(self, "taxe_editline", None)


def _normalize_tax_option(raw_value):
    value = _safe_float(str(raw_value or "").replace("%", ""))
    candidate = f"{value:.2f}%"
    return candidate if candidate in TAX_OPTIONS else TAX_OPTIONS[0]


def _set_tax_text(self, raw_value=None):
    option = _normalize_tax_option(raw_value)
    widget = _tax_widget(self)
    if widget is None:
        return

    if isinstance(widget, QComboBox):
        if widget.count() == 0:
            widget.addItems(list(TAX_OPTIONS))
        widget.setCurrentText(option)
        return

    widget.setText(option)


def _get_tax_text(self):
    widget = _tax_widget(self)
    if widget is None:
        return TAX_OPTIONS[0]
    if isinstance(widget, QComboBox):
        text = (widget.currentText() or "").strip()
        return text if text else TAX_OPTIONS[0]
    text = (widget.text() or "").strip()
    return text if text else TAX_OPTIONS[0]


def _get_tax_percent(self):
    return _safe_float(_get_tax_text(self).replace("%", "") or 0)


@with_db_session
def _setup_doc_status_combo(self, session=None):
    """Populate status combobox from DB (ordered), with safe fallback values."""
    if not hasattr(self, "status_combobox"):
        return

    self.status_combobox.blockSignals(True)
    self.status_combobox.clear()

    rows = session.execute(
        select(RefStatutDocument.id_statut, RefStatutDocument.libelle_statut)
        .order_by(RefStatutDocument.id_statut)
    ).all()

    if rows:
        for status_id, label in rows:
            self.status_combobox.addItem((label or "").strip(), int(status_id))
    else:
        fallback = [
            (1, "Brouillon"),
            (2, "Valide"),
            (3, "Annule"),
            (4, "Partiel"),
            (5, "Paye"),
        ]
        for status_id, label in fallback:
            self.status_combobox.addItem(label, status_id)

    default_index = 0
    for idx in range(self.status_combobox.count()):
        if _status_label_key(self.status_combobox.itemText(idx)) in ("brouillon", "brouillan"):
            default_index = idx
            break
    self.status_combobox.setCurrentIndex(default_index)
    self.status_combobox.blockSignals(False)


@with_db_session
def _get_selected_status_id(self, session=None):
    """Resolve selected status to a valid ref_statuts_documents id."""
    if not hasattr(self, "status_combobox") or self.status_combobox.count() <= 0:
        status_id = session.execute(
            select(RefStatutDocument.id_statut)
            .where(RefStatutDocument.libelle_statut.like("%Brouillon%"))
            .limit(1)
        ).scalar_one_or_none()
        return int(status_id or 1)

    selected_data = self.status_combobox.currentData()
    if selected_data is not None:
        try:
            return int(selected_data)
        except (TypeError, ValueError):
            pass

    selected_label = (self.status_combobox.currentText() or "").strip()
    if selected_label:
        rows = session.execute(
            select(RefStatutDocument.id_statut, RefStatutDocument.libelle_statut)
        ).all()
        wanted = _status_label_key(selected_label)
        for status_id, db_label in rows:
            if _status_label_key(db_label) == wanted:
                return int(status_id)

    return 1


@with_db_session
def _cleanup_empty_new_document(self, session=None):
    """Delete a newly-created document if it has no active detail lines."""
    document_id = getattr(self, "current_document_id", None)
    if not document_id:
        return

    # Do not auto-delete when user opened an existing document.
    if bool(getattr(self, "_opened_existing_document", False)):
        return

    active_details_count = session.execute(
        select(DetailDocument.id_detail)
        .where(
            and_(
                DetailDocument.id_document == document_id,
                DetailDocument.doc_actif == 1,
            )
        )
    ).scalars().all()

    if active_details_count:
        return

    session.execute(delete(Document).where(Document.id_document == document_id))
    session.commit()

    self.current_document_id = None


def _install_close_cleanup(self):
    """Install a one-time closeEvent hook to cleanup empty documents."""
    if getattr(self, "_empty_doc_close_cleanup_installed", False):
        return

    original_close_event = getattr(self, "closeEvent", None)

    def _wrapped_close_event(event):
        _cleanup_empty_new_document(self)
        if callable(original_close_event):
            original_close_event(event)
        else:
            event.accept()

    self.closeEvent = _wrapped_close_event
    self._empty_doc_close_cleanup_installed = True







def show_error_message(message_text=None):
    details = "Veuillez vérifier les informations et réessayer."
    full_message = f"{message_text}" if message_text else details
    MessageBox(
        variant="error",
        title="Erreur",
        message=full_message,
    ).exec_()


def _get_ref_text(self):
    if hasattr(self, "productSelector"):
        return self.productSelector.code_edit.text().strip()
    return self.articles_combobox.text().strip()


def _get_designation_text(self):
    if hasattr(self, "productSelector"):
        return self.productSelector.desc_edit.text().strip()
    return self.designation_editline.text().strip()


def _set_product_fields(self, ref="", designation=""):
    if hasattr(self, "productSelector"):
        self.productSelector.code_edit.setText(ref or "")
        self.productSelector.desc_edit.setText(designation or "")
    else:
        self.articles_combobox.setText(ref or "")
        self.designation_editline.setText(designation or "")


def _clear_product_fields(self):
    if hasattr(self, "productSelector"):
        self.productSelector.clear_selection()
    else:
        self.articles_combobox.clear()
        self.designation_editline.clear()

@with_db_session
def _valider(self, session=None):
    tiers_type = (getattr(self, "tiers_type_filter", None) or "CLIENT").strip() or "CLIENT"
    tiers_label = (getattr(self, "tiers_label", None) or ("Fournisseur" if tiers_type == "FOURNISSEUR" else "Client")).strip()
    domain_id = int(getattr(self, "doc_domain_id", 1) or 1)

    id_tiers = session.execute(
        select(Tiers.id_tiers)
        .where(
            and_(
                Tiers.nom_tiers == self.clients_lineedit.text().strip(),
                Tiers.code_tiers == self.clientid_lineedit.text().strip(),
                Tiers.type_tiers == tiers_type,
            )
        )
    ).scalar_one_or_none()

    if not id_tiers:
        # Try to auto-fix: partial match on code first, then partial match on name
        code_input = self.clientid_lineedit.text().strip()
        name_input = self.clients_lineedit.text().strip()

        lookup_filter = None
        if code_input:
            lookup_filter = and_(
                Tiers.type_tiers == tiers_type,
                Tiers.code_tiers.like(f"%{code_input}%"),
            )
        elif name_input:
            lookup_filter = and_(
                Tiers.type_tiers == tiers_type,
                Tiers.nom_tiers.like(f"%{name_input}%"),
            )

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
                    and_(
                        Tiers.nom_tiers == row.nom_tiers,
                        Tiers.code_tiers == row.code_tiers,
                        Tiers.type_tiers == tiers_type,
                    )
                )
            ).scalar_one_or_none()
        else:
            self.clients_lineedit.clear()
            self.clientid_lineedit.clear()
            show_error_message(f"{tiers_label} introuvable. Veuillez sélectionner un {tiers_label.lower()} valide.")
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

    selected_status_id = _get_selected_status_id(self)

    document = Document(
        id_domaine=domain_id,
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
        id_statut=selected_status_id,
        commentaire=""
    )

    session.add(document)
    session.flush()

    log_audit_event(
        session,
        table_name=Document.__tablename__,
        record_id=int(document.id_document),
        action="INSERT",
        new_values={
            "numero_document": (numero_document or "").strip() or None,
            "id_domaine": int(domain_id),
            "id_type_document": int(id_type_document),
            "id_tiers": int(id_tiers),
            "id_statut": int(selected_status_id),
        },
        comment=f"Création document: {(numero_document or '').strip()}".strip(),
    )


    self._clients_autocomplete.set_enabled(False)
    self.clientid_lineedit.setReadOnly(True)
    self.date_dateedit.setReadOnly(True)
    if hasattr(self, "status_combobox"):
        self.status_combobox.setEnabled(False)
    self.valider_button.setEnabled(False)

    # Unlock article entry fields and action buttons
    self._set_entry_fields_enabled(True)

    self.current_document_id = document.id_document

def _recalculate_entry(self):
    """Recalculate the per-line Total TTC preview field."""
    try:
        puht = _safe_float(self.puht_editline.text() or 0)
        qte = _safe_float(self.qte_lineedit.text() or 1)
        taxe = _get_tax_percent(self) / 100
        pttc = puht * (1 + taxe)
        total = pttc * qte
        self.pttc_editline.setText(f"{pttc:.2f}")
        self.ttc_lineedit.setText(f"{total:.2f}")
    except ValueError:
        self.ttc_lineedit.setText("")

def _on_annuler(self):
    """Clear the article entry fields."""
    _clear_product_fields(self)
    self.puht_editline.clear()
    self.pttc_editline.clear()
    self.qte_lineedit.setText("1")
    _set_tax_text(self, TAX_OPTIONS[0])
    self.ttc_lineedit.clear()
    self._editing_detail_id = None

    if hasattr(self, "productSelector"):
        self.productSelector.setEnabled(True)
    else:
        self.articles_combobox.setReadOnly(False)

@with_db_session
def _on_supprimer(self, session=None):
    """Remove the currently selected row from the table."""
    selected_rows = self.tableWidget.selectionModel().selectedRows() if self.tableWidget.selectionModel() else []
    if selected_rows:
        row = selected_rows[0].row()
        id_detail_item = self.tableWidget.item(row, 7)  # Hidden ID Detail column
        if id_detail_item:
            id_detail = (id_detail_item.text() or "").strip()
            session.execute(
                delete(DetailDocument).where(
                    (DetailDocument.id_detail == id_detail) &
                    (DetailDocument.id_document == self.current_document_id)
                )
            )

            numero_document = (self.ndocument_lineedit.text() if hasattr(self, "ndocument_lineedit") else "").strip()
            try:
                detail_id_int = int(str(id_detail).strip())
            except Exception:
                detail_id_int = None

            log_audit_event(
                session,
                table_name=DetailDocument.__tablename__,
                record_id=detail_id_int if detail_id_int is not None else str(id_detail),
                action="DELETE",
                comment=f"Suppression d'une ligne du document {numero_document} : détail #{id_detail}".strip(),
                new_values={"id_document": int(self.current_document_id), "numero_document": numero_document or None},
            )
            session.commit()
            self.tableWidget.removeRow(row)
            _recalculate_totals(self)
    _on_annuler(self)
        
@with_db_session
def _on_enregistrer(self, session=None):
    """Insert a new line or update the selected one."""
    if not self.current_document_id:
        show_error_message("Veuillez valider le document avant d'ajouter des lignes.")
        return

    ref_text = _get_ref_text(self)
    desig = _get_designation_text(self)

    try:
        ref = ref_text
        puht = _safe_float(self.puht_editline.text() or 0)
        pttc = _safe_float(self.pttc_editline.text() or 0)
        qte = _safe_float(self.qte_lineedit.text() or 1)
        taxe = _get_tax_percent(self)
        total = _safe_float(self.ttc_lineedit.text() or 0)
    except ValueError:
        show_error_message("Ligne invalide. Vérifiez la référence article, les prix, la quantité et la taxe.")
        return

    query = select(Article.id_article).where(Article.reference_interne == ref)
    id_article = session.execute(query).scalar_one_or_none()
    if not id_article:
        show_error_message(f"Article avec référence '{ref}' introuvable.")
        return

    editing_detail_id = getattr(self, "_editing_detail_id", None)
    qte_display = (
        str(int(qte))
        if isinstance(qte, (int, float)) and float(qte).is_integer()
        else str(qte)
    )

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
        detail = DetailDocument(
            id_document=int(self.current_document_id),
            id_article=int(id_article),
            description=desig,
            prix_unitaire_ht=puht,
            prix_unitaire_ttc=pttc,
            quantite=qte,
            taux_tva=taxe,
            total_ligne_ttc=total,
        )
        session.add(detail)

    if editing_detail_id:
        session.execute(query)
        detail_record_id = int(editing_detail_id)
        detail_action = "UPDATE"
        detail_comment = f"Modification d'une ligne du document {{numero}} : {ref} × {qte_display}".strip()
    else:
        session.flush()
        detail_record_id = int(getattr(detail, "id_detail", 0) or 0)
        detail_action = "INSERT"
        detail_comment = f"Ajout d'une ligne au document {{numero}} : {ref} × {qte_display}".strip()

    numero_document = (self.ndocument_lineedit.text() if hasattr(self, "ndocument_lineedit") else "").strip()
    log_audit_event(
        session,
        table_name=DetailDocument.__tablename__,
        record_id=detail_record_id if detail_record_id else str(detail_record_id),
        action=detail_action,
        comment=detail_comment.format(numero=numero_document),
        new_values={
            "id_document": int(self.current_document_id),
            "numero_document": numero_document or None,
            "reference_article": ref,
            "quantite": qte,
        },
    )
    session.commit()
    _reload_table(self)


@with_db_session
def _reload_table(self, session=None):
    was_sorting_enabled = self.tableWidget.isSortingEnabled()
    sort_section = self.tableWidget.horizontalHeader().sortIndicatorSection()
    sort_order = self.tableWidget.horizontalHeader().sortIndicatorOrder()

    if was_sorting_enabled:
        self.tableWidget.setSortingEnabled(False)

    self.tableWidget.setRowCount(0)  # Clear and reload to show the new line with its ID
    query = (
        select(DetailDocument)
        .where(
            (DetailDocument.id_document == self.current_document_id) &
            (DetailDocument.doc_actif == 1)
        )
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
            is_numeric = col in (2, 3, 4, 5, 6)
            item = _build_detail_item(
                value,
                align_right=(col not in (0, 1)),
                numeric=is_numeric,
                quantity=(col == 4),
            )
            self.tableWidget.setItem(row, col, item)

    if was_sorting_enabled:
        self.tableWidget.setSortingEnabled(True)
        if sort_section is not None and int(sort_section) >= 0:
            self.tableWidget.sortItems(int(sort_section), sort_order)

    _recalculate_totals(self)
    _on_annuler(self)  # clear entry fields after adding

def _on_nouveau(self):
    """Reset the entire document form."""
    _cleanup_empty_new_document(self)

    self.tableWidget.setRowCount(0)
    _on_annuler(self)
    self.date_dateedit.setDate(QDate.currentDate())
    self.clientid_lineedit.clear()
    self.clients_lineedit.clear()
    _set_tax_text(self, TAX_OPTIONS[0])
    self.total_tax_label.setText("0.00")
    self.total_UT_label.setText("0.00")
    self.total_ttc_label.setText("0.00")
    _update_table_stats(self)
    self._clients_autocomplete.set_enabled(True)  # Re-enable for next document
    self.clientid_lineedit.setReadOnly(False)
    self.date_dateedit.setReadOnly(False)
    if hasattr(self, "status_combobox"):
        self.status_combobox.setEnabled(True)
        for idx in range(self.status_combobox.count()):
            if _status_label_key(self.status_combobox.itemText(idx)) in ("brouillon", "brouillan"):
                self.status_combobox.setCurrentIndex(idx)
                break
    self.valider_button.setEnabled(True)
    self._set_entry_fields_enabled(False)  # Lock article fields
    self.current_document_id = None

    # Always prepare a fresh document number (do not clear it)
    self.ndocument_lineedit.setText(generate_document_number(self.current_doc_type))
    self.ndocument_lineedit.setReadOnly(True)

@with_db_session
def _recalculate_totals(self, session=None):
    """Recompute footer totals from the table rows."""
    total_ht = 0.0
    total_tax = 0.0
    total_ttc = 0.0
    for row in range(self.tableWidget.rowCount()):
        try:
            puht = _safe_float((self.tableWidget.item(row, 2) or QTableWidgetItem("0")).text() or 0)
            qte = _safe_float((self.tableWidget.item(row, 4) or QTableWidgetItem("1")).text() or 1)
            taxe_text = (self.tableWidget.item(row, 5) or QTableWidgetItem("0%")).text().replace("%", "")
            taxe = _safe_float(taxe_text) / 100
            ht = puht * qte
            tax = ht * taxe
            total_ht += ht
            total_tax += tax
            total_ttc += ht + tax
        except ValueError:
            continue
    self.total_UT_label.setText(_format_amount(total_ht))
    self.total_tax_label.setText(_format_amount(total_tax))
    self.total_ttc_label.setText(_format_amount(total_ttc))
    _update_table_stats(self)

    query = update(Document).where(Document.id_document == self.current_document_id).values(
        total_ht=float(total_ht),
        total_tva=float(total_tax),
        total_ttc=float(total_ttc),
        solde=float(total_ttc)
    )
    session.execute(query)
    session.commit()


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

    _set_product_fields(self, ref, designation)
    self.puht_editline.setText(f"{_safe_float(puht):.2f}")
    self.pttc_editline.setText(f"{_safe_float(pttc):.2f}")
    qte_value = _safe_float(qte)
    self.qte_lineedit.setText(str(int(qte_value)) if qte_value.is_integer() else f"{qte_value:g}")
    _set_tax_text(self, taxe)
    self.ttc_lineedit.setText(f"{_safe_float(total):.2f}")
    self._editing_detail_id = id_detail or None

    if hasattr(self, "productSelector"):
        self.productSelector.setEnabled(True)
    else:
        self.articles_combobox.setReadOnly(True)
    _update_table_stats(self)


@with_db_session
def _connect_signals(self, session=None):
    """Wire up button signals."""
    for signal, handler in (
        (self.annule.clicked, lambda: _on_annuler(self)),
        (self.suprimer.clicked, lambda: _on_supprimer(self)),
        (self.enrgistrer.clicked, lambda: _on_enregistrer(self)),
        (self.btn_fermer.clicked, self.close),
        (self.btn_nouveau.clicked, lambda: _on_nouveau(self)),
        (self.tableWidget.itemSelectionChanged, lambda: _on_table_row_selected(self)),
    ):
        try:
            signal.disconnect()
        except TypeError:
            pass
        signal.connect(handler)

    for signal in (self.puht_editline.textChanged, self.qte_lineedit.textChanged):
        try:
            signal.disconnect()
        except TypeError:
            pass
        signal.connect(lambda: _recalculate_entry(self))

    tax_widget = _tax_widget(self)
    if tax_widget is not None:
        tax_signal = tax_widget.currentTextChanged if isinstance(tax_widget, QComboBox) else tax_widget.textChanged
        try:
            tax_signal.disconnect()
        except TypeError:
            pass
        tax_signal.connect(lambda _value=None: _recalculate_entry(self))

    if hasattr(self, "productSelector"):
        try:
            self.productSelector.productSelected.disconnect()
        except TypeError:
            pass
        self.productSelector.productSelected.connect(lambda product: _on_product_selected_from_selector(self, product))

        for line_widget in (self.productSelector.code_edit, self.productSelector.desc_edit):
            try:
                line_widget.returnPressed.disconnect()
            except TypeError:
                pass
            line_widget.returnPressed.connect(lambda: _commit_current_line_from_keyboard(self))
    else:
        try:
            self.articles_combobox.returnPressed.disconnect()
        except TypeError:
            pass
        self.articles_combobox.returnPressed.connect(lambda: _commit_current_line_from_keyboard(self))

        try:
            self.designation_editline.returnPressed.disconnect()
        except TypeError:
            pass
        self.designation_editline.returnPressed.connect(lambda: _commit_current_line_from_keyboard(self))

        try:
            self.articles_combobox.editingFinished.disconnect()
        except TypeError:
            pass
        self.articles_combobox.editingFinished.connect(lambda: ref_tab_func(self))

    for line_name in ("puht_editline", "pttc_editline", "qte_lineedit", "taxe_editline"):
        line_widget = getattr(self, line_name, None)
        if not line_widget or not hasattr(line_widget, "returnPressed"):
            continue
        try:
            line_widget.returnPressed.disconnect()
        except TypeError:
            pass
        line_widget.returnPressed.connect(lambda: _commit_current_line_from_keyboard(self))

    _update_table_stats(self)

def _on_product_selected_from_selector(self, product):
    self.puht_editline.setText(f'{float(product.get("price", 0)):.2f}')
    self.pttc_editline.setText(f'{float(product.get("price_ttc", 0)):.2f}')
    _set_tax_text(self, product.get("tax", 20.0))
    if not self.qte_lineedit.text().strip():
        self.qte_lineedit.setText("1")
    _recalculate_entry(self)


@with_db_session
def _on_designation_return_pressed(self, selected_text=None, session=None):
    return False


def _on_designation_suggestion_selected(self, selected_text):
    return


def _commit_current_line_from_keyboard(self, selected_text=None):
    """Keyboard-first flow: save line."""
    _recalculate_entry(self)
    _on_enregistrer(self)


@with_db_session
def ref_tab_func(self, session=None):
    """Fill linked article fields automatically from selected reference."""
    ref_value = _get_ref_text(self)

    query = select(Article).where(Article.reference_interne == ref_value)
    article = session.execute(query).scalar_one_or_none()

    if article:
        designation = article.nom_article or ""
        if article.description and article.description.strip():
            designation = f"{designation} - {article.description}"

        _set_product_fields(self, ref_value, designation)
        price_field = (getattr(self, "article_price_field", None) or "prix_vente_ht").strip() or "prix_vente_ht"
        price_value = getattr(article, price_field, None)
        self.puht_editline.setText(f"{float(price_value or 0):.2f}")
        _set_tax_text(self, article.taux_tva)
    else:
        self.puht_editline.clear()
        _set_tax_text(self, TAX_OPTIONS[0])

    _recalculate_entry(self)


@with_db_session
def _set_designation_completer(self, session=None):
    return


@with_db_session
def nouveau_doc_setup(self,document_id=None, session=None):
    
    is_existing_document = bool(document_id)

    if not is_existing_document:
        result = self.doc_type_window.exec_()
        if result != QDialog.Accepted:
            return
    parent_widget = self.parentWidget()
    self.setWindowModality(Qt.WindowModal if parent_widget else Qt.ApplicationModal)
    self.show()

    self.tableWidget.setColumnCount(8)  # Adjust column count to include the hidden ID column
    self.tableWidget.setHorizontalHeaderLabels(["Ref", "Désignation", "PU HT", "PU TTC", "Qte", "Taxe", "Total TTC", "ID Detail"])
    self.tableWidget.setColumnHidden(7, True)  # Hide the ID Detail column\
    self.tableWidget.setSortingEnabled(True)
    self.tableWidget.horizontalHeader().setSortIndicatorShown(True)

    _setup_doc_status_combo(self)
    _set_designation_completer(self)
    _connect_signals(self)
    _install_close_cleanup(self)

    self._opened_existing_document = is_existing_document
    _set_tax_text(self, TAX_OPTIONS[0])

    if not is_existing_document:
        self.current_doc_type = self.doc_type_window.get_current_doc_type()
        self.setWindowTitle(f"Nouveau document - {self.current_doc_type}")
        self.ndocument_lineedit.setText(generate_document_number(self.current_doc_type))
        self.ndocument_lineedit.setReadOnly(True)
        try:
            self.valider_button.clicked.disconnect()
        except TypeError:
            pass
        self.valider_button.clicked.connect(lambda: _valider(self))
    else:
        ouvrir_old_doc_setup(self, document_id=document_id)

    self._editing_detail_id = None

    # when focus on ref article combo and I press tab it should fill the designation and the price and the tax of the article and recalculate the total ttc of the line
    

    # you have to link database documents to their tables after creating them, so we load the articles for the new document (which will be empty)

    # and unlink id type tiers and link type tiers only

    # id_type_tiers will be the id to define the clients or the founissers by (CL001 , FR001)

@with_db_session
def ouvrir_old_doc_setup(self, document_id=None, session=None):
    query = select(Document).where(Document.id_document == document_id)
    document = session.execute(query).scalar_one_or_none()
    if not document:
        show_error_message("Document introuvable.")
        self.close()
        return

    apply_context = getattr(self, "apply_document_context", None)
    if callable(apply_context):
        try:
            apply_context(int(getattr(document, "id_domaine", 1) or 1))
        except Exception:
            pass
    self.current_document_id = document_id
    self.current_doc_type = session.execute(select(RefTypeDocument.libelle_type).where(RefTypeDocument.id_type_document == document.id_type_document)).scalar_one_or_none() or "N/A"
    self.setWindowTitle(f"Document - {self.current_doc_type} - {document.numero_document}")
    
    self.clientid_lineedit.setText(session.execute(select(Tiers.code_tiers).where(Tiers.id_tiers == document.id_tiers)).scalar_one_or_none() or "")
    self.clients_lineedit.setText(session.execute(select(Tiers.nom_tiers).where(Tiers.id_tiers == document.id_tiers)).scalar_one_or_none() or "")
    self.ndocument_lineedit.setText(document.numero_document)
    self.date_dateedit.setDate(document.date_document)
    if hasattr(self, "status_combobox"):
        idx_to_select = -1
        for idx in range(self.status_combobox.count()):
            try:
                if int(self.status_combobox.itemData(idx)) == int(document.id_statut):
                    idx_to_select = idx
                    break
            except (TypeError, ValueError):
                continue
        if idx_to_select >= 0:
            self.status_combobox.setCurrentIndex(idx_to_select)
        self.status_combobox.setEnabled(False)
    
    self.ndocument_lineedit.setReadOnly(True)
    self.date_dateedit.setReadOnly(True)
    self.clientid_lineedit.setReadOnly(True)
    self.clients_lineedit.setReadOnly(True)
    self.valider_button.setEnabled(False)
    
    if hasattr(self, "productSelector"):
        self.productSelector.setEnabled(True)
    else:
        self.articles_combobox.setEnabled(True)
        self.designation_editline.setEnabled(True)
    self.puht_editline.setEnabled(True)
    self.pttc_editline.setEnabled(True)
    self.qte_lineedit.setEnabled(True)
    self.taxe_editline.setEnabled(True)

    self.annule.setEnabled(True)
    self.enrgistrer.setEnabled(True)
    self.suprimer.setEnabled(True)


    _reload_table(self)
