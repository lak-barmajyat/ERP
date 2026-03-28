from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox, QDialog, QMenu
from PyQt5.QtCore import Qt, QTimer, QItemSelectionModel, QDate
from datetime import datetime
from program.services import (with_db_session,
                              select,
                              and_,
                              func,
                              RefTypeDocument,
                              Document,
                              Tiers,
                              RefStatutDocument,
                              LineEditAutoComplete,
                              MessageBox)
from program.windows.nouveau_doc import nouveau_doc_setup, NouveauDocWindow
from program.windows.transfer_window import TransfertDocumentDialog


class _NumericSortTableWidgetItem(QTableWidgetItem):
    """Sort using hidden numeric value while keeping original display text."""

    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            left = self.data(Qt.UserRole)
            right = other.data(Qt.UserRole)
            if left is not None and right is not None:
                return float(left) < float(right)
        return super().__lt__(other)


def _create_nouveau_window(self):
    """Create NouveauDocWindow as an owned top-level modal window."""
    parent_window = self.window() if hasattr(self, "window") else None
    window = NouveauDocWindow(parent=parent_window)
    window.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    return window


def _connect_signals(self):
    self.btnFilter.clicked.connect(lambda: _reload_table_total_labels(self))
    if hasattr(self, "btnClearFilters"):
        self.btnClearFilters.clicked.connect(lambda: _clear_filters(self))
    _connect_filter_enter_reload(self)
    self.tableDocuments.itemSelectionChanged.connect(lambda: _sync_checkboxes_from_selection(self))
    _connect_sort_state_tracking(self)
    self.tableDocuments.setContextMenuPolicy(Qt.CustomContextMenu)
    try:
        self.tableDocuments.customContextMenuRequested.disconnect()
    except TypeError:
        pass
    self.tableDocuments.customContextMenuRequested.connect(lambda pos: _on_table_context_menu(self, pos))
    self.tbNew.clicked.connect(lambda: _on_nouveau_clicked(self))
    self.tbEdit.clicked.connect(lambda: _on_modifier_clicked(self))
    self.tbDelete.clicked.connect(lambda: _on_supprimer_clicked(self))
    self.tbDuplicate.clicked.connect(lambda: _on_dupliquer_clicked(self))
    self.tbTransform.clicked.connect(lambda: _on_transformer_clicked(self))
    if hasattr(self, "tbReplace"):
        self.tbReplace.clicked.connect(lambda: _on_remplacer_clicked(self))
    _update_operation_actions_state(self)


def _on_sort_indicator_changed(self, section, order):
    """Remember user sort choice to restore it after auto-reload."""
    self._table_sort_section = int(section)
    self._table_sort_order = order


def _connect_sort_state_tracking(self):
    """Track sort indicator changes on documents table header."""
    if not hasattr(self, "tableDocuments"):
        return

    header = self.tableDocuments.horizontalHeader()
    try:
        header.sortIndicatorChanged.disconnect()
    except TypeError:
        pass
    header.sortIndicatorChanged.connect(lambda section, order: _on_sort_indicator_changed(self, section, order))

    try:
        header.sectionClicked.disconnect()
    except TypeError:
        pass



def _connect_filter_enter_reload(self):
    """Bind Enter/validate actions on filter inputs to trigger reload."""
    for line_name in ("editcodeclient", "editClient", "editDocNumber"):
        line = getattr(self, line_name, None)
        if not line:
            continue
        try:
            line.returnPressed.disconnect()
        except TypeError:
            pass
        line.returnPressed.connect(lambda: _reload_table_total_labels(self))

    for date_name in ("dateFrom", "dateTo"):
        date_edit = getattr(self, date_name, None)
        if not date_edit:
            continue
        try:
            date_edit.editingFinished.disconnect()
        except TypeError:
            pass
        date_edit.editingFinished.connect(lambda: _reload_table_total_labels(self))

    for combo_name in ("comboDocType", "comboStatus"):
        combo = getattr(self, combo_name, None)
        if not combo:
            continue
        try:
            combo.activated.disconnect()
        except TypeError:
            pass
        combo.activated.connect(lambda _idx: _reload_table_total_labels(self))


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

    # If several clients match the typed name, keep code empty to avoid narrowing to a single client.
    matching_codes = session.execute(
        select(Tiers.code_tiers)
        .where(
            and_(
                Tiers.type_tiers == "CLIENT",
                Tiers.nom_tiers.like(f"%{value}%"),
            )
        )
        .order_by(Tiers.nom_tiers)
        .limit(2)
    ).scalars().all()

    code = (matching_codes[0] or "") if len(matching_codes) == 1 else ""

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
        selected_rows = {idx.row() for idx in selection_model.selectedRows()}
        if row not in selected_rows:
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
    action_transferer = menu.addAction("Transférer")
    action_remplacer = menu.addAction("Remplacer")

    selected_docs_count = len(_get_selected_documents(self))
    action_dupliquer.setEnabled(selected_docs_count == 1)
    action_remplacer.setEnabled(selected_docs_count == 1)

    picked = menu.exec_(self.tableDocuments.viewport().mapToGlobal(pos))
    if picked == action_modifier:
        _on_modifier_clicked(self)
    elif picked == action_supprimer:
        _on_supprimer_clicked(self)
    elif picked == action_dupliquer:
        _on_dupliquer_clicked(self)
    elif picked == action_transferer:
        _on_transformer_clicked(self)
    elif picked == action_remplacer:
        _on_remplacer_clicked(self)


def _on_dupliquer_clicked(self):
    """Open transfer window in duplicate mode for selected document."""
    documents = _get_selected_documents(self)
    if not documents:
        MessageBox(
            variant="info",
            title="Dupliquer",
            message="Veuillez sélectionner un document à dupliquer.",
            parent=self,
        ).exec_()
        return

    if len(documents) > 1:
        MessageBox(
            variant="info",
            title="Dupliquer",
            message="Veuillez sélectionner un seul document pour la duplication.",
            parent=self,
        ).exec_()
        return

    source_doc = documents[0]
    parent_window = self.window() if hasattr(self, "window") else None
    dialog = TransfertDocumentDialog(
        parent=parent_window,
        source_doc_id=source_doc["id"],
        source_doc_number=source_doc["number"],
        default_operation="duplicate",
    )
    dialog.exec_()
    _reload_table_total_labels(self)


def _on_transformer_clicked(self):
    """Open transfer dialog for the currently selected document."""
    documents = _get_selected_documents(self)
    if not documents:
        MessageBox(
            variant="info",
            title="Transférer",
            message="Veuillez sélectionner un document à transférer.",
            parent=self,
        ).exec_()
        return

    selected_doc_ids = {doc["id"] for doc in documents}
    selected_type_labels = []
    for row in range(self.tableDocuments.rowCount()):
        id_item = self.tableDocuments.item(row, 9)
        type_item = self.tableDocuments.item(row, 1)
        if not id_item or not type_item:
            continue
        try:
            row_doc_id = int((id_item.text() or "").strip())
        except ValueError:
            continue
        if row_doc_id in selected_doc_ids:
            selected_type_labels.append((type_item.text() or "").strip().casefold())

    if any("avoir" in label for label in selected_type_labels):
        MessageBox(
            variant="info",
            title="Transférer",
            message="Aucun type de destination disponible pour un document Avoir.",
            parent=self,
        ).exec_()
        return

    unique_types = {label for label in selected_type_labels if label}
    if len(unique_types) > 1:
        MessageBox(
            variant="info",
            title="Transférer",
            message="Les documents sélectionnés doivent être du même type pour un transfert groupé.",
            parent=self,
        ).exec_()
        return

    parent_window = self.window() if hasattr(self, "window") else None
    if len(documents) > 1:
        dialog = TransfertDocumentDialog(
            parent=parent_window,
            source_docs=documents,
            default_operation="transfer",
        )
    else:
        source_doc = documents[0]
        dialog = TransfertDocumentDialog(
            parent=parent_window,
            source_doc_id=source_doc["id"],
            source_doc_number=source_doc["number"],
            default_operation="transfer",
        )
    dialog.exec_()
    _reload_table_total_labels(self)


def _on_remplacer_clicked(self):
    """Open transfer dialog in replace mode for selected document."""
    documents = _get_selected_documents(self)
    if not documents:
        MessageBox(
            variant="info",
            title="Remplacer",
            message="Veuillez sélectionner un document à remplacer.",
            parent=self,
        ).exec_()
        return

    if len(documents) > 1:
        MessageBox(
            variant="info",
            title="Remplacer",
            message="Veuillez sélectionner un seul document pour le remplacement.",
            parent=self,
        ).exec_()
        return

    source_doc = documents[0]
    parent_window = self.window() if hasattr(self, "window") else None
    dialog = TransfertDocumentDialog(
        parent=parent_window,
        source_doc_id=source_doc["id"],
        source_doc_number=source_doc["number"],
        default_operation="replace",
    )
    dialog.exec_()
    _reload_table_total_labels(self)

def _start_auto_refresh(self):
    """Auto-refresh documents list every 10 seconds."""
    if not hasattr(self, "_refresh_timer"):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10000)
        self._refresh_timer.timeout.connect(lambda: _reload_table_total_labels(self))

    if not self._refresh_timer.isActive():
        self._refresh_timer.start()


def _set_sync_guard(self, value):
    self._checkbox_selection_sync_lock = bool(value)


def _is_sync_guarded(self):
    return bool(getattr(self, "_checkbox_selection_sync_lock", False))


def _find_row_for_checkbox(self, checkbox):
    if checkbox is None or not hasattr(self, "tableDocuments"):
        return -1

    for row in range(self.tableDocuments.rowCount()):
        widget = self.tableDocuments.cellWidget(row, 0)
        if widget is checkbox:
            return row
    return -1


def _on_checkbox_state_changed(self, checkbox, state):
    """When a checkbox changes, update row selection accordingly."""
    if _is_sync_guarded(self):
        return

    selection_model = self.tableDocuments.selectionModel()
    if not selection_model:
        return

    row = _find_row_for_checkbox(self, checkbox)
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

    _update_operation_actions_state(self)


def _update_operation_actions_state(self):
    """Enable/disable operation buttons based on selected document count."""
    selected_count = len(_get_selected_documents(self))
    has_selection = selected_count > 0
    single_selection = selected_count == 1

    if hasattr(self, "tbTransform"):
        self.tbTransform.setEnabled(has_selection)
    if hasattr(self, "tbDuplicate"):
        self.tbDuplicate.setEnabled(single_selection)
    if hasattr(self, "tbReplace"):
        self.tbReplace.setEnabled(single_selection)


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


def _clear_filters(self):
    """Reset all filters to default values and reload table."""
    self.editcodeclient.clear()
    self.editClient.clear()
    self.editDocNumber.clear()

    self.comboDocType.setCurrentIndex(0)
    self.comboStatus.setCurrentIndex(0)

    today = datetime.today().date()
    self.dateFrom.setDate(QDate(today.year - 10, today.month, today.day))
    self.dateTo.setDate(QDate.currentDate())

    _reload_table_total_labels(self)


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


def _render_rows(self, rows_data):
    """Render rows into tableDocuments from normalized row dictionaries."""
    was_sorting_enabled = self.tableDocuments.isSortingEnabled() if hasattr(self, "tableDocuments") else False
    sort_section = getattr(self, "_table_sort_section", None)
    sort_order = getattr(self, "_table_sort_order", Qt.AscendingOrder)

    if sort_section is None and hasattr(self, "tableDocuments"):
        sort_section = self.tableDocuments.horizontalHeader().sortIndicatorSection()
        sort_order = self.tableDocuments.horizontalHeader().sortIndicatorOrder()

    self.tableDocuments.setUpdatesEnabled(False)

    if was_sorting_enabled:
        self.tableDocuments.setSortingEnabled(False)

    current_col_count = self.tableDocuments.columnCount()
    if current_col_count < 10:
        self.tableDocuments.setColumnCount(10)  # 9 visible + 1 hidden for ID
        self.tableDocuments.setHorizontalHeaderItem(9, QTableWidgetItem("ID"))
        self.tableDocuments.setColumnHidden(9, True)

    self.tableDocuments.setRowCount(len(rows_data))

    for row, row_data in enumerate(rows_data):
        checkbox = QCheckBox()
        self.tableDocuments.setCellWidget(row, 0, checkbox)
        checkbox.stateChanged.connect(lambda state, cb=checkbox: _on_checkbox_state_changed(self, cb, state))

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
            is_numeric = col in (4, 5, 6)
            item = _build_table_item(
                value,
                align_right=(col not in (0, 1, 2, 3, 7)),
                numeric=is_numeric,
            )
            self.tableDocuments.setItem(row, col + 1, item)

        # Save client code in item metadata for in-memory filtering.
        client_item = self.tableDocuments.item(row, 4)
        if client_item:
            client_item.setData(Qt.UserRole, row_data.get("code_client", ""))

    _sync_checkboxes_from_selection(self)

    if was_sorting_enabled:
        # Set the sort indicator BEFORE enabling sorting to prevent Qt from auto-emitting
        # sortIndicatorChanged(0, ...) which would overwrite our stored sort state.
        if sort_section is not None and int(sort_section) >= 0:
            header = self.tableDocuments.horizontalHeader()
            header.setSortIndicator(int(sort_section), sort_order)
        
        self.tableDocuments.setSortingEnabled(True)
        if sort_section is not None and int(sort_section) >= 0:
            self.tableDocuments.sortItems(int(sort_section), sort_order)

    self.tableDocuments.setUpdatesEnabled(True)


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


def _capture_table_scroll_position(self):
    """Capture current scroll position of documents table."""
    if not hasattr(self, "tableDocuments"):
        return {"vertical": 0, "horizontal": 0}

    return {
        "vertical": self.tableDocuments.verticalScrollBar().value(),
        "horizontal": self.tableDocuments.horizontalScrollBar().value(),
    }


def _restore_table_scroll_position(self, position):
    """Restore scroll position after table reload."""
    if not hasattr(self, "tableDocuments"):
        return

    if not isinstance(position, dict):
        return

    self.tableDocuments.verticalScrollBar().setValue(int(position.get("vertical", 0)))
    self.tableDocuments.horizontalScrollBar().setValue(int(position.get("horizontal", 0)))


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


def _format_number(value):
    """Format number with thousands separators and exactly 2 decimals."""
    return f"{_safe_float(value):,.2f}"


def _build_table_item(value, align_right=False, numeric=False):
    """Create a table item with optional numeric sort role."""
    if numeric:
        display_text = _format_number(value)
        item = _NumericSortTableWidgetItem(display_text)
        item.setData(Qt.UserRole, _safe_float(value))
    else:
        display_text = str(value if value is not None else "")
        item = QTableWidgetItem(display_text)

    item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if align_right else Qt.AlignLeft))

    return item


def _set_total_labels_from_rows(self, rows_data):
    """Fast totals from in-memory normalized rows, avoids table text parsing."""
    self.labelNbDocumentsValue.setText(str(len(rows_data)))

    total_ht = sum(float(row.get("total_ht") or 0) for row in rows_data)
    total_ttc = sum(float(row.get("total_ttc") or 0) for row in rows_data)
    total_balance = sum(float(row.get("solde") or 0) for row in rows_data)

    self.labelTotalHtValue.setText(_format_number(total_ht))
    self.labelTotalTtcValue.setText(_format_number(total_ttc))
    self.labelTotalBalanceValue.setText(_format_number(total_balance))

@with_db_session
def _reload_table_total_labels(self, session=None):
    # Fetch only filtered rows from DB (SQL-side filtering) for better performance.
    selected_ids = _capture_selected_document_ids(self)
    scroll_position = _capture_table_scroll_position(self)
    filters = _collect_filter_values(self)

    vente_codes = ["DV", "BC", "BL", "FA", "AV"]
    query = (
        select(
            Document.id_document,
            Document.numero_document,
            Document.date_document,
            Document.total_ht,
            Document.total_ttc,
            Document.solde,
            Document.id_tiers,
            Document.id_statut,
            RefTypeDocument.libelle_type,
            Tiers.nom_tiers,
            Tiers.code_tiers,
            RefStatutDocument.libelle_statut,
        )
        .join(RefTypeDocument, Document.id_type_document == RefTypeDocument.id_type_document)
        .outerjoin(Tiers, Document.id_tiers == Tiers.id_tiers)
        .join(RefStatutDocument, Document.id_statut == RefStatutDocument.id_statut)
        .where(
            and_(
                Document.id_domaine == 1,
                Document.doc_actif == 1,
                RefTypeDocument.code_type.in_(vente_codes),
            )
        )
    )

    if filters["date_from"]:
        query = query.where(Document.date_document >= filters["date_from"])
    if filters["date_to"]:
        query = query.where(Document.date_document <= filters["date_to"])
    if filters["code_client"]:
        query = query.where(func.lower(Tiers.code_tiers).like(f"%{filters['code_client']}%"))
    if filters["client"]:
        query = query.where(func.lower(Tiers.nom_tiers).like(f"%{filters['client']}%"))
    if filters["doc_number"]:
        query = query.where(func.lower(Document.numero_document).like(f"%{filters['doc_number']}%"))
    if filters["doc_type"]:
        query = query.where(func.lower(RefTypeDocument.libelle_type).like(f"%{filters['doc_type']}%"))
    if filters["status"]:
        query = query.where(func.lower(RefStatutDocument.libelle_statut) == filters["status"])

    query = query.order_by(Document.id_document.desc())

    docs = session.execute(query).all()

    if not docs:
        self.tableDocuments.setRowCount(0)
        _set_total_labels_from_rows(self, [])
        _restore_table_scroll_position(self, scroll_position)
        return

    rows_data = []
    for doc in docs:
        rows_data.append({
            "type": doc.libelle_type or "N/A",
            "doc_number": doc.numero_document,
            "date": doc.date_document.strftime("%Y-%m-%d") if doc.date_document else "",
            "client": doc.nom_tiers or "N/A",
            "code_client": doc.code_tiers or "",
            "total_ht": float(doc.total_ht or 0),
            "total_ttc": float(doc.total_ttc or 0),
            "solde": float(doc.solde or 0),
            "status": doc.libelle_statut or "N/A",
            "id_document": doc.id_document,
        })

    _render_rows(self, rows_data)
    _restore_selection_by_ids(self, selected_ids)
    _restore_table_scroll_position(self, scroll_position)
    _set_total_labels_from_rows(self, rows_data)


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
    if not selection_model and self.tableDocuments.rowCount() <= 0:
        return []

    selected_docs = []
    selected_rows = selection_model.selectedRows() if selection_model else []

    # Fallback 1: current row when selection model has no selected rows.
    if not selected_rows and self.tableDocuments.currentRow() >= 0:
        selected_rows = [self.tableDocuments.model().index(self.tableDocuments.currentRow(), 1)]

    # Fallback 2: checked rows when no highlighted row exists.
    if not selected_rows:
        for row in range(self.tableDocuments.rowCount()):
            checkbox = self.tableDocuments.cellWidget(row, 0)
            if not isinstance(checkbox, QCheckBox) or not checkbox.isChecked():
                continue
            selected_rows.append(self.tableDocuments.model().index(row, 1))

    for index in selected_rows:
        if not index.isValid():
            continue
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
    """Soft-delete one or many selected documents (doc_actif = 0)."""
    documents = _get_selected_documents(self)
    if not documents:
        MessageBox(
            variant="info",
            title="Supprimer",
            message="Veuillez sélectionner un document à supprimer.",
            parent=self,
        ).exec_()
        return

    archived_count = 0
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

        document = session.execute(
            select(Document).where(Document.id_document == document_id)
        ).scalar_one_or_none()

        if not document or int(document.doc_actif or 0) == 0:
            skipped_count += 1
            continue

        document.doc_actif = 0
        archived_count += 1

    if archived_count > 0:
        session.commit()

    _reload_table_total_labels(self)

    if skipped_count > 0:
        MessageBox(
            variant="attention",
            title="Suppression partielle",
            message=f"{archived_count} document(s) supprimé(s), {skipped_count} ignoré(s).",
            parent=self,
        ).exec_()

def liste_ventes_setup(self):
    _setup_client_filter_autocomplete(self)
    _reload_table_total_labels(self)
    _connect_signals(self)
    _start_auto_refresh(self)
    self.tableDocuments.cellDoubleClicked.connect(lambda row, col: _open_document_from_row(self, row, col))