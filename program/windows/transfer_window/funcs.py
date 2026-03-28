from datetime import datetime
import os

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel, QSizePolicy, QTableWidgetItem, QWidget

from program.services import (
    Article,
    DetailDocument,
    Document,
    MessageBox,
    RefTypeDocument,
    Tiers,
    and_,
    generate_document_number,
    select,
    with_db_session,
)


TRANSFER = "transfer"
DUPLICATE = "duplicate"
REPLACE = "replace"


def _fmt_amount(value) -> str:
    try:
        return f"{float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _fmt_qty(value) -> str:
    try:
        qty = float(value or 0)
    except (TypeError, ValueError):
        return "0"
    return f"{int(round(qty)):,d}"


def _show_error(self, message: str) -> None:
    MessageBox(variant="error", title="Opération document", message=message, parent=self).exec_()


def _show_success(self, message: str) -> None:
    MessageBox(variant="success", title="Opération document", message=message, parent=self).exec_()


def _op_key_from_text(text: str) -> str:
    value = (text or "").strip().lower()
    if value.startswith("transfer") or value.startswith("transf"):
        return TRANSFER
    if value.startswith("dub") or value.startswith("dup") or value.startswith("dupli"):
        return DUPLICATE
    if value.startswith("remp") or value.startswith("rempl") or value.startswith("repl") or value.startswith("replace"):
        return REPLACE
    return TRANSFER


def _current_operation(self) -> str:
    op = getattr(self, "_default_operation", TRANSFER)
    return op if op in (TRANSFER, DUPLICATE, REPLACE) else TRANSFER


def _checkbox_cell(checked=True, on_toggled=None):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignCenter)
    checkbox = QCheckBox(container)
    checkbox.setChecked(bool(checked))
    if on_toggled is not None:
        checkbox.toggled.connect(on_toggled)
    layout.addWidget(checkbox)
    return container


def _styled_total_pill(title: str, object_name: str):
    frame = QFrame()
    frame.setStyleSheet(
        "QFrame { background-color: #ffffff; border: 1px solid rgba(196,197,215,0.55); "
        "border-radius: 8px; padding: 4px 10px; }"
    )
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(10, 6, 10, 6)
    layout.setSpacing(8)

    title_label = QLabel(title)
    title_label.setStyleSheet("color: #57657a; font: 700 8pt 'Overpass';")

    value_label = QLabel("0.00 MAD")
    value_label.setObjectName(object_name)
    value_label.setStyleSheet("color: #1d7ae2; font: 800 10pt 'Overpass';")

    layout.addWidget(title_label)
    layout.addWidget(value_label)
    return frame, value_label


def _ensure_totals_footer(self):
    if hasattr(self, "_transferTotalsFooter"):
        return

    details_layout = getattr(self, "detailsLayout", None)
    if not details_layout:
        return

    footer = QFrame(self)
    footer.setObjectName("transferTotalsFooter")
    footer.setStyleSheet("QFrame#transferTotalsFooter { background-color: transparent; border: none; }")
    footer_layout = QHBoxLayout(footer)
    footer_layout.setContentsMargins(4, 4, 4, 0)
    footer_layout.setSpacing(8)

    footer_layout.addStretch(1)

    ht_pill, self.labelTransferTotalHT = _styled_total_pill("TOTAL HT", "labelTransferTotalHT")
    tva_pill, self.labelTransferTotalTVA = _styled_total_pill("TOTAL TVA", "labelTransferTotalTVA")
    ttc_pill, self.labelTransferTotalTTC = _styled_total_pill("TOTAL TTC", "labelTransferTotalTTC")

    footer_layout.addWidget(ht_pill)
    footer_layout.addWidget(tva_pill)
    footer_layout.addWidget(ttc_pill)

    details_layout.addWidget(footer)
    self._transferTotalsFooter = footer


def _configure_table(self):
    if not hasattr(self, "tableTransferDetails"):
        return

    self.tableTransferDetails.setStyleSheet(
        """
QTableWidget#tableTransferDetails {
    background-color: #ffffff;
    border: none;
    gridline-color: #e2e8f0;
    font: 400 9pt "Overpass";
    color: #374151;
    selection-background-color: rgba(19,91,236,0.08);
    selection-color: #111827;
    outline: 0;
}
QTableWidget#tableTransferDetails::item {
    padding: 6px 10px;
    border-bottom: 1px solid #f3f4f6;
}
QTableWidget#tableTransferDetails::item:alternate {
    background-color: #f9fafb;
}
QTableWidget#tableTransferDetails::item:selected {
    background-color: rgba(19,91,236,0.08);
    color: #111827;
}
QTableWidget#tableTransferDetails::item:hover {
    background-color: #f9fafb;
}
QHeaderView::section {
    background-color: #f9fafb;
    color: #374151;
    font: 600 9pt "Overpass";
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 2px solid #e2e8f0;
}
QHeaderView::section:last {
    border-right: none;
}
"""
    )

    self.tableTransferDetails.setAlternatingRowColors(True)
    self.tableTransferDetails.setShowGrid(False)
    self.tableTransferDetails.verticalHeader().setVisible(False)
    self.tableTransferDetails.setSortingEnabled(True)
    self.tableTransferDetails.setColumnCount(5)
    self.tableTransferDetails.setHorizontalHeaderLabels([
        "",
        "Référence",
        "Désignation",
        "Qté",
        "Prix unitaire",
    ])

    header = self.tableTransferDetails.horizontalHeader()
    header.setSectionsClickable(True)
    header.setSortIndicatorShown(True)
    header.setStretchLastSection(False)
    header.setSectionResizeMode(0, header.Fixed)
    header.setSectionResizeMode(1, header.ResizeToContents)
    header.setSectionResizeMode(2, header.Stretch)
    header.setSectionResizeMode(3, header.ResizeToContents)
    header.setSectionResizeMode(4, header.ResizeToContents)
    self.tableTransferDetails.setColumnWidth(0, 38)


def _set_source_card(self, document, source_type_code: str, source_type_label: str, source_client_name: str):
    if hasattr(self, "label_13"):
        self.label_13.setText(document.numero_document or "N/A")
        self.label_13.setToolTip("")
        self.label_13.setWordWrap(False)
    if hasattr(self, "label_14"):
        self.label_14.setText(source_client_name or "N/A")
    if hasattr(self, "label_15"):
        try:
            self.label_15.setText(f"Émis le {document.date_document.strftime('%d/%m/%Y')}")
        except Exception:
            self.label_15.setText("Date indisponible")
    if hasattr(self, "label_16"):
        badge = (source_type_label or source_type_code or "").upper()
        self.label_16.setText(f" {badge} ")


def _set_source_card_multi(self, source_numbers, source_type_code: str, source_type_label: str, source_client_name: str):
    numbers = [n for n in (source_numbers or []) if n]
    if hasattr(self, "label_13"):
        if numbers:
            preview = ", ".join(numbers[:3])
            if len(numbers) > 3:
                self.label_13.setText(f"{preview}\n+ {len(numbers) - 3} autre(s)")
            else:
                self.label_13.setText(preview)
            self.label_13.setToolTip(" | ".join(numbers))
        else:
            self.label_13.setText("N/A")
            self.label_13.setToolTip("")
        self.label_13.setWordWrap(True)
        self.label_13.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    if hasattr(self, "label_14"):
        self.label_14.setText(source_client_name or "N/A")
    if hasattr(self, "label_15"):
        count = len(numbers)
        self.label_15.setText(f"{count} document(s) source")
    if hasattr(self, "label_16"):
        badge = (source_type_label or source_type_code or "").upper()
        self.label_16.setText(f" {badge} ")


def _get_allowed_target_codes(source_code: str):
    code = (source_code or "").upper().strip()
    rules = {
        "DV": ["BC", "BL", "FA"],
        "BC": ["BL", "FA"],
        "BL": ["FA"],
        "FA": ["AV"],
    }
    return rules.get(code, [])


def _all_duplicate_codes():
    return ["DV", "BC", "BL", "FA", "AV"]


@with_db_session
def _populate_clients(self, selected_client_id=None, session=None):
    if not hasattr(self, "comboClient"):
        return

    self.comboClient.blockSignals(True)
    self.comboClient.clear()

    rows = session.execute(
        select(Tiers.id_tiers, Tiers.nom_tiers)
        .where(Tiers.type_tiers == "CLIENT")
        .order_by(Tiers.nom_tiers)
    ).all()

    for id_tiers, nom_tiers in rows:
        self.comboClient.addItem(nom_tiers or "N/A", id_tiers)

    if selected_client_id is not None:
        idx = self.comboClient.findData(selected_client_id)
        if idx >= 0:
            self.comboClient.setCurrentIndex(idx)

    self.comboClient.blockSignals(False)


@with_db_session
def _resolve_target_client_id(self, session=None):
    if not hasattr(self, "comboClient"):
        return None

    current_data = self.comboClient.currentData()
    if current_data is not None:
        try:
            return int(current_data)
        except (TypeError, ValueError):
            pass

    typed_name = (self.comboClient.currentText() or "").strip()
    if not typed_name:
        return None

    client_id = session.execute(
        select(Tiers.id_tiers)
        .where(
            and_(
                Tiers.type_tiers == "CLIENT",
                Tiers.nom_tiers == typed_name,
            )
        )
        .limit(1)
    ).scalar_one_or_none()

    if client_id:
        return int(client_id)

    client_id = session.execute(
        select(Tiers.id_tiers)
        .where(
            and_(
                Tiers.type_tiers == "CLIENT",
                Tiers.nom_tiers.like(f"%{typed_name}%"),
            )
        )
        .order_by(Tiers.nom_tiers)
        .limit(1)
    ).scalar_one_or_none()

    return int(client_id) if client_id else None


def _set_button_text_for_operation(self):
    if not hasattr(self, "btnLaunchTransfer"):
        return

    op = _current_operation(self)
    if op == DUPLICATE:
        self.btnLaunchTransfer.setText("Dupliquer")
    elif op == REPLACE:
        self.btnLaunchTransfer.setText("Remplacer")
    else:
        self.btnLaunchTransfer.setText("Transférer")


def _apply_operation_chrome(self):
    """Update title bar texts according to the fixed operation mode."""
    op = _current_operation(self)

    if op == DUPLICATE:
        op_label = "Dupliquer"
        window_title = "Dupliquer un document"
    elif op == REPLACE:
        op_label = "Remplacer"
        window_title = "Remplacer un document"
    else:
        op_label = "Transférer"
        window_title = "Transférer un document"

    if hasattr(self, "labelTitlePrefix"):
        self.labelTitlePrefix.setText(f"Opération: {op_label}")

    self.setWindowTitle(window_title)


def _set_operation_defaults(self, default_operation=None):
    op = _op_key_from_text(default_operation or "")
    self._default_operation = op

    if hasattr(self, "dateTarget_2"):
        self.dateTarget_2.setDate(QDate.currentDate())

    if hasattr(self, "RefEditline"):
        self.RefEditline.setReadOnly(False)

    if hasattr(self, "comboClient"):
        self.comboClient.setEditable(True)

    _apply_operation_chrome(self)
    _set_button_text_for_operation(self)


def _apply_mode_ui_rules(self):
    """Apply destination and details interactivity rules by operation mode."""
    op = _current_operation(self)

    if hasattr(self, "dateTarget_2"):
        self.dateTarget_2.setDate(QDate.currentDate())

    if hasattr(self, "comboClient"):
        self.comboClient.setEditable(True)
        self.comboClient.setEnabled(op != TRANSFER)

    if hasattr(self, "RefEditline"):
        self.RefEditline.setReadOnly(op == REPLACE)

    if hasattr(self, "comboTypeDoc"):
        self.comboTypeDoc.setEnabled(op != REPLACE)

    select_all_enabled = op != REPLACE
    if hasattr(self, "checkSelectAll"):
        self.checkSelectAll.setEnabled(select_all_enabled)

    if hasattr(self, "tableTransferDetails"):
        for row in range(self.tableTransferDetails.rowCount()):
            widget = self.tableTransferDetails.cellWidget(row, 0)
            if not widget:
                continue
            checkbox = widget.findChild(QCheckBox)
            if not checkbox:
                continue
            if op == REPLACE:
                checkbox.setChecked(True)
            checkbox.setEnabled(select_all_enabled)

    _update_selected_totals(self)


@with_db_session
def _refresh_target_types_and_number(self, session=None):
    if not hasattr(self, "comboTypeDoc"):
        return

    op = _current_operation(self)
    source_code = getattr(self, "_source_type_code", "")

    if op == DUPLICATE:
        allowed_codes = _all_duplicate_codes()
    elif op == TRANSFER:
        allowed_codes = _get_allowed_target_codes(source_code)
    elif op == REPLACE:
        allowed_codes = [source_code] if source_code else []
    else:
        allowed_codes = []

    self.comboTypeDoc.blockSignals(True)
    self.comboTypeDoc.clear()

    if allowed_codes:
        rows = session.execute(
            select(RefTypeDocument.code_type, RefTypeDocument.libelle_type)
            .where(
                and_(
                    RefTypeDocument.code_type.in_(allowed_codes),
                    RefTypeDocument.actif == 1,
                )
            )
            .order_by(RefTypeDocument.ordre, RefTypeDocument.libelle_type)
        ).all()

        for code_type, libelle in rows:
            self.comboTypeDoc.addItem(f"{libelle} ({code_type})", code_type)

    self.comboTypeDoc.blockSignals(False)

    if op == REPLACE:
        if hasattr(self, "RefEditline"):
            self.RefEditline.setText((getattr(self, "_source_doc_number", "") or "").strip())
    else:
        _refresh_target_code(self)


def _refresh_target_code(self):
    if not hasattr(self, "comboTypeDoc") or not hasattr(self, "RefEditline"):
        return

    code_type = (self.comboTypeDoc.currentData() or "").strip()
    if not code_type:
        self.RefEditline.clear()
        return

    try:
        self.RefEditline.setText(generate_document_number(code_type))
    except Exception:
        self.RefEditline.clear()


@with_db_session
def _validate_target_number_available(self, silent=False, session=None):
    if not hasattr(self, "RefEditline") or not hasattr(self, "comboTypeDoc"):
        return True

    numero = self.RefEditline.text().strip()
    code_type = (self.comboTypeDoc.currentData() or "").strip()

    if not numero or not code_type:
        if not silent:
            _show_error(self, "Numéro document et type destination requis.")
        return False

    type_id = session.execute(
        select(RefTypeDocument.id_type_document)
        .where(RefTypeDocument.code_type == code_type)
    ).scalar_one_or_none()

    if not type_id:
        if not silent:
            _show_error(self, "Type destination invalide.")
        return False

    exists = session.execute(
        select(Document.id_document).where(
            and_(
                Document.id_type_document == type_id,
                Document.numero_document == numero,
            )
        )
    ).scalar_one_or_none()
    # Existing numbers are handled at launch time via merge confirmation.
    if exists:
        return True

    return True


def _get_selected_detail_ids(self):
    ids = []
    if not hasattr(self, "tableTransferDetails"):
        return ids

    for row in range(self.tableTransferDetails.rowCount()):
        widget = self.tableTransferDetails.cellWidget(row, 0)
        if not widget:
            continue
        checkbox = widget.findChild(QCheckBox)
        if not checkbox or not checkbox.isChecked():
            continue

        ref_item = self.tableTransferDetails.item(row, 1)
        if not ref_item:
            continue

        detail_id = ref_item.data(Qt.UserRole)
        try:
            ids.append(int(detail_id))
        except (TypeError, ValueError):
            continue

    return ids


def _get_row_totals(self, row: int):
    price_item = self.tableTransferDetails.item(row, 4)
    if not price_item:
        return 0.0, 0.0, 0.0

    try:
        total_ht = float(price_item.data(Qt.UserRole) or 0)
    except (TypeError, ValueError):
        total_ht = 0.0

    try:
        total_tva = float(price_item.data(Qt.UserRole + 1) or 0)
    except (TypeError, ValueError):
        total_tva = 0.0

    try:
        total_ttc = float(price_item.data(Qt.UserRole + 2) or (total_ht + total_tva))
    except (TypeError, ValueError):
        total_ttc = total_ht + total_tva

    return total_ht, total_tva, total_ttc


def _update_selected_totals(self):
    if not hasattr(self, "tableTransferDetails"):
        return

    total_ht = 0.0
    total_tva = 0.0
    total_ttc = 0.0

    for row in range(self.tableTransferDetails.rowCount()):
        widget = self.tableTransferDetails.cellWidget(row, 0)
        if not widget:
            continue
        checkbox = widget.findChild(QCheckBox)
        if not checkbox or not checkbox.isChecked():
            continue

        row_ht, row_tva, row_ttc = _get_row_totals(self, row)
        total_ht += row_ht
        total_tva += row_tva
        total_ttc += row_ttc

    if hasattr(self, "labelTransferTotalHT"):
        self.labelTransferTotalHT.setText(f"{total_ht:,.2f} MAD")
    if hasattr(self, "labelTransferTotalTVA"):
        self.labelTransferTotalTVA.setText(f"{total_tva:,.2f} MAD")
    if hasattr(self, "labelTransferTotalTTC"):
        self.labelTransferTotalTTC.setText(f"{total_ttc:,.2f} MAD")


def _toggle_all_rows(self, checked):
    if not hasattr(self, "tableTransferDetails"):
        return

    for row in range(self.tableTransferDetails.rowCount()):
        widget = self.tableTransferDetails.cellWidget(row, 0)
        if not widget:
            continue
        checkbox = widget.findChild(QCheckBox)
        if checkbox:
            checkbox.setChecked(bool(checked))

    _update_selected_totals(self)


def _populate_details_table(self, detail_rows):
    if not hasattr(self, "tableTransferDetails"):
        return

    was_sorting_enabled = self.tableTransferDetails.isSortingEnabled()
    sort_section = self.tableTransferDetails.horizontalHeader().sortIndicatorSection()
    sort_order = self.tableTransferDetails.horizontalHeader().sortIndicatorOrder()

    if was_sorting_enabled:
        self.tableTransferDetails.setSortingEnabled(False)

    self.tableTransferDetails.setRowCount(0)

    for detail, article_ref, article_desc in detail_rows:
        row = self.tableTransferDetails.rowCount()
        self.tableTransferDetails.insertRow(row)

        self.tableTransferDetails.setCellWidget(
            row,
            0,
            _checkbox_cell(True, lambda _checked=False: _update_selected_totals(self)),
        )

        designation = (detail.description or "").strip() or (article_desc or "")
        row_values = [
            article_ref or "",
            designation,
            _fmt_qty(detail.quantite),
            _fmt_amount(detail.prix_unitaire_ht),
        ]

        for col, value in enumerate(row_values, start=1):
            item = QTableWidgetItem(str(value))
            if col in (3, 4):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if col == 3:
                    item.setData(Qt.EditRole, int(round(float(detail.quantite or 0))))
                else:
                    item.setData(Qt.EditRole, float(detail.prix_unitaire_ht or 0))
            else:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            if col == 1:
                item.setData(Qt.UserRole, int(detail.id_detail))

            if col == 4:
                item.setData(Qt.UserRole, float(detail.total_ligne_ht or 0))
                item.setData(Qt.UserRole + 1, float(detail.total_ligne_tva or 0))
                item.setData(Qt.UserRole + 2, float(detail.total_ligne_ttc or 0))

            self.tableTransferDetails.setItem(row, col, item)

    _update_selected_totals(self)

    if was_sorting_enabled:
        self.tableTransferDetails.setSortingEnabled(True)
        self.tableTransferDetails.sortItems(sort_section, sort_order)


@with_db_session
def _load_source_documents(self, source_doc_ids, source_doc_number=None, session=None):
    source_doc_ids = [int(i) for i in (source_doc_ids or []) if i is not None]
    if not source_doc_ids:
        _show_error(self, "Document source introuvable.")
        return False

    source_rows = session.execute(
        select(
            Document,
            RefTypeDocument.code_type,
            RefTypeDocument.libelle_type,
            Tiers.nom_tiers,
        )
        .join(RefTypeDocument, Document.id_type_document == RefTypeDocument.id_type_document)
        .outerjoin(Tiers, Document.id_tiers == Tiers.id_tiers)
        .where(Document.id_document.in_(source_doc_ids))
        .order_by(Document.id_document)
    ).all()

    if not source_rows:
        _show_error(self, "Document source introuvable.")
        return False

    first_doc = source_rows[0][0]
    source_type_code = source_rows[0][1] or ""
    source_type_label = source_rows[0][2] or ""
    source_client_name = source_rows[0][3] or "N/A"

    # Multi-transfer is only supported for homogeneous source types.
    if any((row[1] or "").upper() != (source_type_code or "").upper() for row in source_rows):
        _show_error(self, "Les documents sélectionnés doivent être du même type pour un transfert groupé.")
        self.reject()
        return False

    self._source_document_ids = [int(row[0].id_document) for row in source_rows]
    self._source_document_id = int(first_doc.id_document)
    self._source_doc_number = (first_doc.numero_document or "").strip()
    self._source_type_code = source_type_code

    if len(source_rows) > 1:
        numbers = [(row[0].numero_document or "").strip() for row in source_rows]
        _set_source_card_multi(self, numbers, source_type_code, source_type_label, source_client_name)
    else:
        _set_source_card(self, first_doc, source_type_code, source_type_label, source_client_name)

    _populate_clients(self, selected_client_id=first_doc.id_tiers)

    detail_rows = session.execute(
        select(DetailDocument, Article.reference_interne, Article.description)
        .outerjoin(Article, DetailDocument.id_article == Article.id_article)
        .where(
            and_(
                DetailDocument.id_document.in_(self._source_document_ids),
                DetailDocument.doc_actif == 1,
            )
        )
        .order_by(DetailDocument.id_document, DetailDocument.id_detail)
    ).all()

    _populate_details_table(self, detail_rows)
    _refresh_target_types_and_number(self)

    if getattr(self, "_default_operation", TRANSFER) == TRANSFER and (source_type_code or "").upper() == "AV":
        MessageBox(
            variant="info",
            title="Transférer",
            message="Aucun type de destination disponible pour un document Avoir.",
            parent=self,
        ).exec_()
        self.reject()
        return False

    return True


def _apply_operation_mode(self):
    """Apply one-time operation behavior for current window invocation."""
    _apply_operation_chrome(self)
    _set_button_text_for_operation(self)
    _refresh_target_types_and_number(self)
    _apply_mode_ui_rules(self)


def _recompute_active_doc_totals(doc_id: int, session):
    active_details = session.execute(
        select(DetailDocument).where(
            and_(
                DetailDocument.id_document == doc_id,
                DetailDocument.doc_actif == 1,
            )
        )
    ).scalars().all()

    total_ht = sum(float(d.total_ligne_ht or 0) for d in active_details)
    total_tva = sum(float(d.total_ligne_tva or 0) for d in active_details)
    total_ttc = sum(float(d.total_ligne_ttc or 0) for d in active_details)

    return total_ht, total_tva, total_ttc, len(active_details)


def _create_new_document_from_selection(self, source_doc, target_type_id: int, target_client_id: int, selected_details, session):
    total_ht = sum(float(d.total_ligne_ht or 0) for d in selected_details)
    total_tva = sum(float(d.total_ligne_tva or 0) for d in selected_details)
    total_ttc = sum(float(d.total_ligne_ttc or 0) for d in selected_details)

    new_doc = Document(
        id_domaine=source_doc.id_domaine,
        id_type_document=target_type_id,
        numero_document=self.RefEditline.text().strip(),
        id_tiers=target_client_id,
        date_document=self.dateTarget_2.date().toPyDate(),
        date_livraison=datetime.now().date(),
        mode_prix=source_doc.mode_prix,
        total_ht=total_ht,
        total_tva=total_tva,
        total_ttc=total_ttc,
        solde=total_ttc,
        id_vendeur=int(os.getenv("USER_ID", str(source_doc.id_vendeur or 6))),
        id_statut=source_doc.id_statut,
        commentaire=source_doc.commentaire,
        doc_actif=1,
        id_precedent_doc=source_doc.id_document,
    )

    session.add(new_doc)
    session.flush()

    for old_detail in selected_details:
        session.add(
            DetailDocument(
                id_document=new_doc.id_document,
                id_article=old_detail.id_article,
                description=old_detail.description,
                quantite=old_detail.quantite,
                prix_unitaire_ht=old_detail.prix_unitaire_ht,
                prix_unitaire_ttc=old_detail.prix_unitaire_ttc,
                unite_vente=old_detail.unite_vente,
                taux_tva=old_detail.taux_tva,
                marge_beneficiaire=old_detail.marge_beneficiaire,
                total_ligne_ht=old_detail.total_ligne_ht,
                total_ligne_tva=old_detail.total_ligne_tva,
                total_ligne_ttc=old_detail.total_ligne_ttc,
                id_precedent_doc=old_detail.id_document,
                doc_actif=1,
            )
        )

    return new_doc


@with_db_session
def _execute_operation(self, session=None):
    op = _current_operation(self)

    source_doc_ids = getattr(self, "_source_document_ids", None) or []
    if not source_doc_ids:
        source_doc_id = getattr(self, "_source_document_id", None)
        if source_doc_id:
            source_doc_ids = [int(source_doc_id)]

    if not source_doc_ids:
        _show_error(self, "Document source invalide.")
        return

    if len(source_doc_ids) > 1 and op != TRANSFER:
        _show_error(self, "Le transfert groupé multi-documents est disponible uniquement en mode Transférer.")
        return

    source_doc = session.execute(
        select(Document).where(Document.id_document == source_doc_ids[0])
    ).scalar_one_or_none()
    if not source_doc:
        _show_error(self, "Document source introuvable.")
        return

    if op == REPLACE:
        target_client_id = _resolve_target_client_id(self)
        if not target_client_id:
            _show_error(self, "Client destination invalide.")
            return

        source_doc.id_tiers = target_client_id
        if hasattr(self, "dateTarget_2"):
            source_doc.date_document = self.dateTarget_2.date().toPyDate()
        source_doc.date_livraison = datetime.now().date()

        session.commit()
        _show_success(self, f"Document remplacé: {source_doc.numero_document}")
        self.accept()
        return

    if not _validate_target_number_available(self):
        return

    target_code = (self.comboTypeDoc.currentData() or "").strip()
    if not target_code:
        _show_error(self, "Type document destination requis.")
        return

    selected_detail_ids = _get_selected_detail_ids(self)
    if not selected_detail_ids:
        _show_error(self, "Veuillez sélectionner au moins une ligne.")
        return

    target_type_id = session.execute(
        select(RefTypeDocument.id_type_document).where(RefTypeDocument.code_type == target_code)
    ).scalar_one_or_none()
    if not target_type_id:
        _show_error(self, "Type destination introuvable.")
        return

    target_doc_number = (self.RefEditline.text() or "").strip()
    existing_target_doc = None
    if target_type_id and target_doc_number:
        existing_target_doc = session.execute(
            select(Document).where(
                and_(
                    Document.id_type_document == int(target_type_id),
                    Document.numero_document == target_doc_number,
                )
            )
        ).scalar_one_or_none()

    merge_into_existing = False
    if existing_target_doc is not None:
        if int(existing_target_doc.id_document) in {int(i) for i in source_doc_ids}:
            _show_error(self, "Le document destination ne peut pas être identique au document source.")
            return

        answer = MessageBox(
            variant="question",
            title="Document existant",
            message=(
                f"Le numéro '{target_doc_number}' existe déjà.\n"
                "Voulez-vous fusionner les lignes sélectionnées dans ce document ?"
            ),
            parent=self,
        ).exec_()

        if answer != QDialog.Accepted:
            return

        merge_into_existing = True

    selected_details = session.execute(
        select(DetailDocument)
        .where(
            and_(
                DetailDocument.id_document.in_(source_doc_ids),
                DetailDocument.id_detail.in_(selected_detail_ids),
                DetailDocument.doc_actif == 1,
            )
        )
        .order_by(DetailDocument.id_document, DetailDocument.id_detail)
    ).scalars().all()

    if not selected_details:
        _show_error(self, "Aucune ligne active valide à traiter.")
        return

    if op == TRANSFER:
        target_client_id = source_doc.id_tiers
    else:
        target_client_id = _resolve_target_client_id(self)
        if not target_client_id:
            _show_error(self, "Client destination invalide.")
            return

    target_doc = None
    if merge_into_existing:
        target_doc = existing_target_doc
        for old_detail in selected_details:
            session.add(
                DetailDocument(
                    id_document=target_doc.id_document,
                    id_article=old_detail.id_article,
                    description=old_detail.description,
                    quantite=old_detail.quantite,
                    prix_unitaire_ht=old_detail.prix_unitaire_ht,
                    prix_unitaire_ttc=old_detail.prix_unitaire_ttc,
                    unite_vente=old_detail.unite_vente,
                    taux_tva=old_detail.taux_tva,
                    marge_beneficiaire=old_detail.marge_beneficiaire,
                    total_ligne_ht=old_detail.total_ligne_ht,
                    total_ligne_tva=old_detail.total_ligne_tva,
                    total_ligne_ttc=old_detail.total_ligne_ttc,
                    id_precedent_doc=old_detail.id_document,
                    doc_actif=1,
                )
            )
    else:
        target_doc = _create_new_document_from_selection(
            self,
            source_doc=source_doc,
            target_type_id=target_type_id,
            target_client_id=target_client_id,
            selected_details=selected_details,
            session=session,
        )

    if op == TRANSFER:
        for old_detail in selected_details:
            old_detail.doc_actif = 0

        # Session is configured with autoflush=False, so flush before re-querying active lines.
        session.flush()

        touched_source_ids = sorted({int(d.id_document) for d in selected_details})
        for touched_doc_id in touched_source_ids:
            old_doc = session.execute(
                select(Document).where(Document.id_document == touched_doc_id)
            ).scalar_one_or_none()
            if not old_doc:
                continue

            remaining_ht, remaining_tva, remaining_ttc, remaining_count = _recompute_active_doc_totals(touched_doc_id, session)

            if remaining_count == 0:
                old_doc.doc_actif = 0
            else:
                old_doc.total_ht = remaining_ht
                old_doc.total_tva = remaining_tva
                old_doc.total_ttc = remaining_ttc
                old_doc.solde = remaining_ttc

    # Recompute destination document totals in both create and merge paths.
    session.flush()
    dst_ht, dst_tva, dst_ttc, _dst_count = _recompute_active_doc_totals(int(target_doc.id_document), session)
    target_doc.total_ht = dst_ht
    target_doc.total_tva = dst_tva
    target_doc.total_ttc = dst_ttc
    target_doc.solde = dst_ttc

    session.commit()

    if merge_into_existing:
        if op == DUPLICATE:
            _show_success(self, f"Document fusionné (duplication): {target_doc_number}")
        else:
            _show_success(self, f"Document fusionné (transfert): {target_doc_number}")
    else:
        if op == DUPLICATE:
            _show_success(self, f"Document dupliqué: {target_doc_number}")
        else:
            _show_success(self, f"Document transféré: {target_doc_number}")

    self.accept()


def _connect_signals(self):
    if hasattr(self, "btnClose"):
        try:
            self.btnClose.clicked.disconnect()
        except TypeError:
            pass
        self.btnClose.clicked.connect(self.close)

    if hasattr(self, "btnCancel"):
        try:
            self.btnCancel.clicked.disconnect()
        except TypeError:
            pass
        self.btnCancel.clicked.connect(self.reject)

    if hasattr(self, "btnLaunchTransfer"):
        try:
            self.btnLaunchTransfer.clicked.disconnect()
        except TypeError:
            pass
        self.btnLaunchTransfer.clicked.connect(lambda: _execute_operation(self))

    if hasattr(self, "checkSelectAll"):
        try:
            self.checkSelectAll.toggled.disconnect()
        except TypeError:
            pass
        self.checkSelectAll.toggled.connect(lambda checked: _toggle_all_rows(self, checked))

    if hasattr(self, "comboTypeDoc"):
        try:
            self.comboTypeDoc.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.comboTypeDoc.currentIndexChanged.connect(lambda _: _refresh_target_code(self))

    if hasattr(self, "RefEditline"):
        try:
            self.RefEditline.editingFinished.disconnect()
        except TypeError:
            pass
        self.RefEditline.editingFinished.connect(lambda: _validate_target_number_available(self, silent=False))

def transfer_window_setup(self, source_doc_id=None, source_doc_number=None, source_docs=None, default_operation="transfer"):
    _configure_table(self)
    _ensure_totals_footer(self)
    _set_operation_defaults(self, default_operation=default_operation)
    _connect_signals(self)

    if hasattr(self, "dateTarget_2"):
        self.dateTarget_2.setDate(QDate.currentDate())

    source_ids = []
    if source_docs:
        source_ids = [int(doc.get("id")) for doc in source_docs if doc.get("id") is not None]
    elif source_doc_id is not None:
        source_ids = [int(source_doc_id)]

    if source_ids:
        loaded = _load_source_documents(self, source_doc_ids=source_ids, source_doc_number=source_doc_number)
        if not loaded:
            return
        _apply_operation_mode(self)
        return

    _show_error(self, "Aucun document source sélectionné.")
