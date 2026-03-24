from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox, QDialog, QMenu
from PyQt5.QtCore import Qt, QTimer, QItemSelectionModel
from datetime import datetime
from program.services import (with_db_session,
                              select,
                              delete,
                              and_,
                              RefTypeDocument,
                              Document,
                              Tiers,
                              RefStatutDocument,
                              LineEditAutoComplete,
                              MessageBox)
from program.windows.nouveau_doc import nouveau_doc_setup, NouveauDocWindow


def _create_nouveau_window(self):
    """Create NouveauDocWindow as an owned top-level modal window."""
    parent_window = self.window() if hasattr(self, "window") else None
    window = NouveauDocWindow(parent=parent_window)
    window.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    return window


def _connect_signals(self):
    self.btnFilter.clicked.connect(lambda: _filter_from_current_table(self))
    self.tableDocuments.itemSelectionChanged.connect(lambda: _sync_checkboxes_from_selection(self))
    self.tableDocuments.setContextMenuPolicy(Qt.CustomContextMenu)
    try:
        self.tableDocuments.customContextMenuRequested.disconnect()
    except TypeError:
        pass
    self.tableDocuments.customContextMenuRequested.connect(lambda pos: _on_table_context_menu(self, pos))
    if hasattr(self, "tbNew"):
        try:
            self.tbNew.clicked.disconnect()
        except TypeError:
            pass
        self.tbNew.clicked.connect(lambda: _on_nouveau_clicked(self))
    if hasattr(self, "tbEdit"):
        try:
            self.tbEdit.clicked.disconnect()
        except TypeError:
            pass
        self.tbEdit.clicked.connect(lambda: _on_modifier_clicked(self))
    if hasattr(self, "tbDelete"):
        try:
            self.tbDelete.clicked.disconnect()
        except TypeError:
            pass
        self.tbDelete.clicked.connect(lambda: _on_supprimer_clicked(self))
    if hasattr(self, "tbDuplicate"):
        try:
            self.tbDuplicate.clicked.disconnect()
        except TypeError:
            pass
        self.tbDuplicate.clicked.connect(lambda: _on_dupliquer_clicked(self))
    if hasattr(self, "tbTransform"):
        try:
            self.tbTransform.clicked.disconnect()
        except TypeError:
            pass
        self.tbTransform.clicked.connect(lambda: _on_transformer_clicked(self))


@with_db_session
def _setup_client_filter_autocomplete(self, session=None):
    """Apply nouveau_doc-like autocomplete to client-name filter and sync code/name fields."""
    if not hasattr(self, "editClient") or not hasattr(self, "editcodeclient"):
        return

    self._filter_client_autocomplete = LineEditAutoComplete(self.editClient, self)

    names = session.execute(
        select(Tiers.nom_tiers)
        .where(Tiers.type_tiers == "CLIENT")
        .order_by(Tiers.nom_tiers)
    ).scalars().all()
    self._filter_client_autocomplete.set_items([name for name in names if name])

    try:
        self.editClient.textChanged.disconnect()
    except TypeError:
        pass
    self.editClient.textChanged.connect(lambda text: _sync_client_code_from_name(self, text))

    try:
        self.editcodeclient.textChanged.disconnect()
    except TypeError:
        pass
    self.editcodeclient.textChanged.connect(lambda text: _sync_client_name_from_code(self, text))


@with_db_session
def _sync_client_code_from_name(self, name_text, session=None):
    """When typing client name, auto-fill matching client code."""
    if not hasattr(self, "editClient") or not hasattr(self, "editcodeclient"):
        return
    if not self.editClient.hasFocus():
        return

    value = (name_text or "").strip()
    if value == "":
        self.editcodeclient.blockSignals(True)
        self.editcodeclient.clear()
        self.editcodeclient.blockSignals(False)
        return

    code = session.execute(
        select(Tiers.code_tiers)
        .where(
            and_(
                Tiers.type_tiers == "CLIENT",
                Tiers.nom_tiers.like(f"%{value}%"),
            )
        )
        .order_by(Tiers.nom_tiers)
        .limit(1)
    ).scalar_one_or_none() or ""

    self.editcodeclient.blockSignals(True)
    self.editcodeclient.setText(code)
    self.editcodeclient.blockSignals(False)


@with_db_session
def _sync_client_name_from_code(self, code_text, session=None):
    """When typing client code, auto-fill matching client name."""
    if not hasattr(self, "editClient") or not hasattr(self, "editcodeclient"):
        return
    if not self.editcodeclient.hasFocus():
        return

    value = (code_text or "").strip()
    if value == "":
        self.editClient.blockSignals(True)
        self.editClient.clear()
        self.editClient.blockSignals(False)
        return

    name = session.execute(
        select(Tiers.nom_tiers)
        .where(
            and_(
                Tiers.type_tiers == "CLIENT",
                Tiers.code_tiers.like(f"%{value}%"),
            )
        )
        .order_by(Tiers.nom_tiers)
        .limit(1)
    ).scalar_one_or_none() or ""

    self.editClient.blockSignals(True)
    self.editClient.setText(name)
    self.editClient.blockSignals(False)


def _on_table_context_menu(self, pos):
    """Show contextual actions for the row under mouse cursor."""
    index = self.tableDocuments.indexAt(pos)
    if not index.isValid():
        return

    row = index.row()
    target_index = self.tableDocuments.model().index(row, 1)
    selection_model = self.tableDocuments.selectionModel()
    if selection_model and target_index.isValid():
        selection_model.select(target_index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        selection_model.setCurrentIndex(target_index, QItemSelectionModel.NoUpdate)

    menu = QMenu(self.tableDocuments)
    menu.setMinimumWidth(220)
    menu.setStyleSheet(
        """
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 3px;
            font: 600 9pt "Overpass";
            color: #374151;
        }
        QMenu::item {
            padding: 3px 8px;
            border-radius: 6px;
            min-width: 180px;
        }
        QMenu::item:selected {
            background-color: #eef4ff;
            color: #135bec;
        }
        QMenu::separator {
            height: 1px;
            margin: 6px 8px;
            background: #e5e7eb;
        }
        """
    )
    action_modifier = menu.addAction("Modifier")
    action_supprimer = menu.addAction("Supprimer")
    menu.addSeparator()
    action_dupliquer = menu.addAction("Dupliquer")
    action_transformer = menu.addAction("Transformer")

    picked = menu.exec_(self.tableDocuments.viewport().mapToGlobal(pos))
    if picked == action_modifier:
        _on_modifier_clicked(self)
    elif picked == action_supprimer:
        _on_supprimer_clicked(self)
    elif picked == action_dupliquer:
        _on_dupliquer_clicked(self)
    elif picked == action_transformer:
        _on_transformer_clicked(self)


def _on_dupliquer_clicked(self):
    """Placeholder duplicate action until business rules are finalized."""
    document_id = _get_selected_document_id(self)
    if not document_id:
        MessageBox(
            variant="info",
            title="Dupliquer",
            message="Veuillez sélectionner un document à dupliquer.",
            parent=self,
        ).exec_()
        return

    MessageBox(
        variant="attention",
        title="Dupliquer",
        message="La duplication du document sera disponible dans la prochaine version.",
        parent=self,
    ).exec_()


def _on_transformer_clicked(self):
    """Placeholder transform action until workflow rules are finalized."""
    document_id = _get_selected_document_id(self)
    if not document_id:
        MessageBox(
            variant="info",
            title="Transformer",
            message="Veuillez sélectionner un document à transformer.",
            parent=self,
        ).exec_()
        return

    MessageBox(
        variant="attention",
        title="Transformer",
        message="La transformation du document sera disponible dans la prochaine version.",
        parent=self,
    ).exec_()

def _start_auto_refresh(self):
    """Auto-refresh documents list every 5 seconds."""
    if not hasattr(self, "_refresh_timer"):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(5000)
        self._refresh_timer.timeout.connect(lambda: _reload_table_total_labels(self))

    if not self._refresh_timer.isActive():
        self._refresh_timer.start()


def _set_sync_guard(self, value):
    self._checkbox_selection_sync_lock = bool(value)


def _is_sync_guarded(self):
    return bool(getattr(self, "_checkbox_selection_sync_lock", False))


def _on_checkbox_state_changed(self, row, state):
    """When a checkbox changes, update row selection accordingly."""
    if _is_sync_guarded(self):
        return

    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return

    row = int(row)
    if row < 0 or row >= self.tableDocuments.rowCount():
        return

    index = self.tableDocuments.model().index(row, 1)
    if not index.isValid():
        return

    _set_sync_guard(self, True)
    try:
        if state == Qt.Checked:
            selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            self.tableDocuments.setCurrentCell(row, 1)
        else:
            selection_model.select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
    finally:
        _set_sync_guard(self, False)


def _sync_checkboxes_from_selection(self):
    """When row selection changes, mirror it to row checkboxes."""
    if _is_sync_guarded(self):
        return

    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return

    selected_rows = {index.row() for index in selection_model.selectedRows()}

    _set_sync_guard(self, True)
    try:
        for row in range(self.tableDocuments.rowCount()):
            checkbox = self.tableDocuments.cellWidget(row, 0)
            if not isinstance(checkbox, QCheckBox):
                continue
            should_check = row in selected_rows
            checkbox.blockSignals(True)
            checkbox.setChecked(should_check)
            checkbox.blockSignals(False)
    finally:
        _set_sync_guard(self, False)


def _collect_filter_values(self):
    """Read current filter widgets and normalize values."""
    status_text = (self.comboStatus.currentText() or "").strip()
    doc_type_text = (self.comboDocType.currentText() or "").strip() if hasattr(self, "comboDocType") else ""
    return {
        "code_client": (self.editcodeclient.text() or "").strip().casefold(),
        "client": (self.editClient.text() or "").strip().casefold(),
        "doc_number": (self.editDocNumber.text() or "").strip().casefold(),
        "date_from": self.dateFrom.date().toPyDate() if hasattr(self, "dateFrom") else None,
        "date_to": self.dateTo.date().toPyDate() if hasattr(self, "dateTo") else None,
        "doc_type": "" if doc_type_text.casefold() == "tous les types" else doc_type_text.casefold(),
        "status": "" if status_text.casefold() == "tous les statuts" else status_text.casefold(),
    }


def _parse_row_date(date_text):
    """Support both 'YYYY-MM-DD' and 'dd/MM/yyyy' date string formats."""
    value = (date_text or "").strip()
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _row_matches_filters(row_data, filters):
    doc_type = (row_data.get("type") or "").casefold()
    code_client = (row_data.get("code_client") or "").casefold()
    client = (row_data.get("client") or "").casefold()
    doc_number = (row_data.get("doc_number") or "").casefold()
    status = (row_data.get("status") or "").casefold()

    if filters["doc_type"] and filters["doc_type"] not in doc_type:
        return False
    if filters["code_client"] and filters["code_client"] not in code_client:
        return False
    if filters["client"] and filters["client"] not in client:
        return False
    if filters["doc_number"] and filters["doc_number"] not in doc_number:
        return False
    if filters["status"] and filters["status"] != status:
        return False

    row_date = _parse_row_date(row_data.get("date"))
    if row_date is not None:
        if filters["date_from"] and row_date < filters["date_from"]:
            return False
        if filters["date_to"] and row_date > filters["date_to"]:
            return False

    return True


def _render_rows(self, rows_data):
    """Render rows into tableDocuments from normalized row dictionaries."""
    self.tableDocuments.setRowCount(0)

    current_col_count = self.tableDocuments.columnCount()
    if current_col_count < 10:
        self.tableDocuments.setColumnCount(10)  # 9 visible + 1 hidden for ID
        self.tableDocuments.setHorizontalHeaderItem(9, QTableWidgetItem("ID"))
        self.tableDocuments.setColumnHidden(9, True)

    for row_data in rows_data:
        row = self.tableDocuments.rowCount()
        self.tableDocuments.insertRow(row)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state, r=row: _on_checkbox_state_changed(self, r, state))
        self.tableDocuments.setCellWidget(row, 0, checkbox)

        visible_values = [
            row_data.get("type", "N/A"),
            row_data.get("doc_number", ""),
            row_data.get("date", ""),
            row_data.get("client", "N/A"),
            row_data.get("total_ht", 0),
            row_data.get("total_ttc", 0),
            row_data.get("solde", 0),
            row_data.get("status", "N/A"),
            row_data.get("id_document", ""),
        ]

        for col, value in enumerate(visible_values):
            item = QTableWidgetItem(str(value if value is not None else ""))
            item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if col not in (0, 1, 2, 3, 7) else Qt.AlignLeft))
            self.tableDocuments.setItem(row, col + 1, item)

        # Save client code in item metadata for in-memory filtering.
        client_item = self.tableDocuments.item(row, 4)
        if client_item:
            client_item.setData(Qt.UserRole, row_data.get("code_client", ""))

    _sync_checkboxes_from_selection(self)


def _capture_selected_document_ids(self):
    """Capture selected document IDs from hidden ID column before refresh."""
    selected_ids = []
    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return selected_ids

    for index in selection_model.selectedRows():
        id_item = self.tableDocuments.item(index.row(), 9)
        if not id_item:
            continue
        doc_id = (id_item.text() or "").strip()
        if doc_id:
            selected_ids.append(doc_id)

    # Fallback for single-current-row scenarios.
    if not selected_ids and self.tableDocuments.currentRow() >= 0:
        id_item = self.tableDocuments.item(self.tableDocuments.currentRow(), 9)
        if id_item:
            doc_id = (id_item.text() or "").strip()
            if doc_id:
                selected_ids.append(doc_id)

    return selected_ids


def _restore_selection_by_ids(self, selected_ids):
    """Restore row selection after refresh using hidden document IDs."""
    if not selected_ids:
        return

    selected_set = set(selected_ids)
    first_selected_row = None
    self.tableDocuments.clearSelection()
    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return

    for row in range(self.tableDocuments.rowCount()):
        id_item = self.tableDocuments.item(row, 9)
        if not id_item:
            continue
        doc_id = (id_item.text() or "").strip()
        if doc_id in selected_set:
            index = self.tableDocuments.model().index(row, 1)
            if index.isValid():
                selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            if first_selected_row is None:
                first_selected_row = row

    if first_selected_row is not None:
        first_index = self.tableDocuments.model().index(first_selected_row, 1)
        if first_index.isValid():
            selection_model.setCurrentIndex(first_index, QItemSelectionModel.NoUpdate)

    _sync_checkboxes_from_selection(self)


def _snapshot_current_table_rows(self):
    """Read currently displayed table rows into dictionaries (no DB access)."""
    rows_data = []
    for row in range(self.tableDocuments.rowCount()):
        client_item = self.tableDocuments.item(row, 4)
        rows_data.append({
            "type": (self.tableDocuments.item(row, 1) or QTableWidgetItem("")).text(),
            "doc_number": (self.tableDocuments.item(row, 2) or QTableWidgetItem("")).text(),
            "date": (self.tableDocuments.item(row, 3) or QTableWidgetItem("")).text(),
            "client": (client_item or QTableWidgetItem("")).text(),
            "code_client": (client_item.data(Qt.UserRole) if client_item else "") or "",
            "total_ht": (self.tableDocuments.item(row, 5) or QTableWidgetItem("0")).text(),
            "total_ttc": (self.tableDocuments.item(row, 6) or QTableWidgetItem("0")).text(),
            "solde": (self.tableDocuments.item(row, 7) or QTableWidgetItem("0")).text(),
            "status": (self.tableDocuments.item(row, 8) or QTableWidgetItem("")).text(),
            "id_document": (self.tableDocuments.item(row, 9) or QTableWidgetItem("")).text(),
        })
    return rows_data


def _filter_from_current_table(self):
    """Apply filters to existing table data only (isolated from database)."""
    selected_ids = _capture_selected_document_ids(self)
    filters = _collect_filter_values(self)
    rows_data = _snapshot_current_table_rows(self)
    filtered_rows = [row for row in rows_data if _row_matches_filters(row, filters)]
    _render_rows(self, filtered_rows)
    _restore_selection_by_ids(self, selected_ids)
    _set_total_labels(self)


def _safe_float(value_text):
    text = str(value_text or "").strip().replace(" ", "").replace(",", ".")
    if text in ("", "-"):
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _set_total_labels(self):
    self.labelNbDocumentsValue.setText(str(self.tableDocuments.rowCount()))

    total_ht = 0.0
    total_ttc = 0.0
    total_balance = 0.0

    for row in range(self.tableDocuments.rowCount()):
        total_ht += _safe_float((self.tableDocuments.item(row, 5) or QTableWidgetItem("0")).text())
        total_ttc += _safe_float((self.tableDocuments.item(row, 6) or QTableWidgetItem("0")).text())
        total_balance += _safe_float((self.tableDocuments.item(row, 7) or QTableWidgetItem("0")).text())

    self.labelTotalHtValue.setText(f"{total_ht:.2f}")
    self.labelTotalTtcValue.setText(f"{total_ttc:.2f}")
    self.labelTotalBalanceValue.setText(f"{total_balance:.2f}")

@with_db_session
def _reload_table_total_labels(self, session=None):
    # Fetch fresh data from DB then apply current UI filters before rendering.
    selected_ids = _capture_selected_document_ids(self)
    query = (
        select(Document).where(Document.id_domaine == 1).order_by(Document.id_document.desc())
    )
    docs = session.execute(query).fetchall()
    if not docs:
        return

    ref_dict = {}
    query = select(RefTypeDocument.id_type_document, RefTypeDocument.libelle_type)
    ref_types = session.execute(query).fetchall()
    for type in ref_types:
        ref_dict[type.id_type_document] = type.libelle_type

    cln_dict = {}
    query = select(Tiers.id_tiers, Tiers.nom_tiers)
    ref_types = session.execute(query).fetchall()
    for type in ref_types:
        cln_dict[type.id_tiers] = type.nom_tiers

    stts_dict = {}
    query = select(RefStatutDocument.id_statut, RefStatutDocument.libelle_statut)
    stts_types = session.execute(query).fetchall()
    for type in stts_types:
        stts_dict[type.id_statut] = type.libelle_statut

    code_dict = {}
    query = select(Tiers.id_tiers, Tiers.code_tiers)
    code_rows = session.execute(query).fetchall()
    for row in code_rows:
        code_dict[row.id_tiers] = row.code_tiers or ""

    rows_data = []
    for doc in docs:
        rows_data.append({
            "type": ref_dict.get(doc.Document.id_type_document, "N/A"),
            "doc_number": doc.Document.numero_document,
            "date": doc.Document.date_document.strftime("%Y-%m-%d"),
            "client": cln_dict.get(doc.Document.id_tiers, "N/A"),
            "code_client": code_dict.get(doc.Document.id_tiers, ""),
            "total_ht": doc.Document.total_ht,
            "total_ttc": doc.Document.total_ttc,
            "solde": doc.Document.solde,
            "status": stts_dict.get(doc.Document.id_statut, "N/A"),
            "id_document": doc.Document.id_document,
        })

    filters = _collect_filter_values(self)
    filtered_rows = [row for row in rows_data if _row_matches_filters(row, filters)]
    _render_rows(self, filtered_rows)
    _restore_selection_by_ids(self, selected_ids)
    _set_total_labels(self)


def _open_document_from_row(self, row, col):
    id_item = self.tableDocuments.item(row, 9)
    if not id_item:
        return

    document_id = (id_item.text() or "").strip()
    if not document_id:
        return

    # Keep a python reference, otherwise window may be garbage-collected and close.
    self._opened_doc_window = _create_nouveau_window(self)
    nouveau_doc_setup(self._opened_doc_window, document_id)


def _on_nouveau_clicked(self):
    """Open a fresh new-document window from the toolbar Nouveau action."""
    self._opened_doc_window = _create_nouveau_window(self)
    nouveau_doc_setup(self._opened_doc_window)


def _get_selected_document_id(self):
    selected_rows = self.tableDocuments.selectionModel().selectedRows() if self.tableDocuments.selectionModel() else []
    if not selected_rows:
        return None

    row = selected_rows[0].row()
    id_item = self.tableDocuments.item(row, 9)
    if not id_item:
        return None

    document_id = (id_item.text() or "").strip()
    if not document_id:
        return None
    try:
        return int(document_id)
    except ValueError:
        return None


def _get_selected_documents(self):
    """Return selected documents as dictionaries with id and displayed reference."""
    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return []

    selected_docs = []
    for index in selection_model.selectedRows():
        id_item = self.tableDocuments.item(index.row(), 9)
        number_item = self.tableDocuments.item(index.row(), 2)
        if not id_item:
            continue
        document_id = (id_item.text() or "").strip()
        if not document_id:
            continue
        try:
            selected_docs.append({
                "id": int(document_id),
                "number": (number_item.text() if number_item else "").strip(),
            })
        except ValueError:
            continue

    # Preserve order while removing duplicates.
    seen = set()
    unique_docs = []
    for doc in selected_docs:
        if doc["id"] in seen:
            continue
        seen.add(doc["id"])
        unique_docs.append(doc)

    return unique_docs


def _on_modifier_clicked(self):
    """Open selected document like table double-click action."""
    document_id = _get_selected_document_id(self)
    if not document_id:
        MessageBox(
            variant="info",
            title="Modifier",
            message="Veuillez sélectionner un document à modifier.",
            parent=self,
        ).exec_()
        return

    self._opened_doc_window = _create_nouveau_window(self)
    nouveau_doc_setup(self._opened_doc_window, str(document_id))


@with_db_session
def _on_supprimer_clicked(self, session=None):
    """Delete one or many selected documents with per-row confirmation."""
    documents = _get_selected_documents(self)
    if not documents:
        MessageBox(
            variant="info",
            title="Supprimer",
            message="Veuillez sélectionner un document à supprimer.",
            parent=self,
        ).exec_()
        return

    deleted_count = 0
    skipped_count = 0

    for doc in documents:
        document_id = doc["id"]
        doc_ref = doc["number"] or f"ID {document_id}"
        answer = MessageBox(
            variant="question",
            title="Confirmation",
            message=f"Supprimer le document {doc_ref} ?",
            parent=self,
        ).exec_()

        if answer != QDialog.Accepted:
            skipped_count += 1
            continue

        session.execute(delete(Document).where(Document.id_document == document_id))
        deleted_count += 1

    if deleted_count > 0:
        session.commit()

    _reload_table_total_labels(self)

    if skipped_count > 0:
        MessageBox(
            variant="attention",
            title="Suppression partielle",
            message=f"{deleted_count} document(s) supprimé(s), {skipped_count} ignoré(s).",
            parent=self,
        ).exec_()

def liste_ventes_setup(self):
    _setup_client_filter_autocomplete(self)
    _reload_table_total_labels(self)
    _connect_signals(self)
    _start_auto_refresh(self)
    self.tableDocuments.cellDoubleClicked.connect(lambda row, col: _open_document_from_row(self, row, col))