import csv
from datetime import datetime

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMenu, QTableWidgetItem

from program.services import Document, MessageBox, Tiers, and_, func, log_audit_event, or_, select, with_db_session
from program.services.sql.db_connection import SessionLocal
from program.themes.shared_input_popup_style import apply_menu_style
from program.windows.nouveau_client import NouveauClientWindow


class _NumericSortTableWidgetItem(QTableWidgetItem):
    """Sort using hidden numeric value while keeping original display text."""

    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            left = self.data(Qt.UserRole)
            right = other.data(Qt.UserRole)
            if left is not None and right is not None:
                return float(left) < float(right)
        return super().__lt__(other)


def _set_loading_state(self, is_loading: bool) -> None:
    """Disable filter controls while loading and show a wait cursor."""
    # Filter inputs
    for name in (
        "btnFilter",
        "tbDuplicate",
        "editSearch",
        "comboType",
        "comboStatus",
        "dateStart",
        "dateEnd",
    ):
        w = getattr(self, name, None)
        if w is None:
            continue
        try:
            w.setEnabled(not is_loading)
        except Exception:
            continue

    try:
        if is_loading:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()
    except Exception:
        return


def _safe_float(value_text) -> float:
    text = str(value_text or "").strip().replace(" ", "")
    if text in ("", "-"):
        return 0.0

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


def _format_amount(value) -> str:
    amount = _safe_float(value)
    # French-ish formatting: space thousands + comma decimals
    text = f"{amount:,.2f}"  # 12,345.67
    return text.replace(",", " ").replace(".", ",")


def _format_int_with_spaces(value: int) -> str:
    return f"{int(value):,}".replace(",", " ")


def _build_checkbox_item(checked: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem("")
    # Keep checkbox cells selectable so clicking them also selects the row.
    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
    item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    item.setTextAlignment(Qt.AlignCenter)
    return item


def _build_table_item(value, *, align_right: bool = False, numeric: bool = False) -> QTableWidgetItem:
    if numeric:
        display_text = _format_amount(value)
        item = _NumericSortTableWidgetItem(display_text)
        item.setData(Qt.UserRole, _safe_float(value))
    else:
        item = QTableWidgetItem(str(value if value is not None else ""))

    item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if align_right else Qt.AlignLeft))
    return item


def _set_sync_guard(self, value: bool) -> None:
    setattr(self, "_checkbox_selection_sync_lock", bool(value))


def _is_sync_guarded(self) -> bool:
    return bool(getattr(self, "_checkbox_selection_sync_lock", False))


def _selected_row_index(self):
    table = getattr(self, "tableClients", None)
    if table is None:
        return None

    selection_model = table.selectionModel()
    selected_rows = selection_model.selectedRows() if selection_model else []
    if not selected_rows:
        return None

    try:
        return int(selected_rows[0].row())
    except Exception:
        return None


def _sync_checkbox_to_selection(self) -> None:
    """Mirror current row selection to the checkbox column (single-selection)."""
    table = getattr(self, "tableClients", None)
    if table is None:
        return

    if _is_sync_guarded(self):
        return

    current_row = _selected_row_index(self)
    current_item = table.item(current_row, 0) if isinstance(current_row, int) else None
    previous_item = getattr(self, "_clients_checkbox_synced_item", None)

    if previous_item is current_item:
        return

    _set_sync_guard(self, True)
    try:
        if previous_item is not None:
            previous_item.setCheckState(Qt.Unchecked)
        if current_item is not None:
            current_item.setCheckState(Qt.Checked)
    finally:
        _set_sync_guard(self, False)

    setattr(self, "_clients_checkbox_synced_item", current_item)


def _on_table_item_changed(self, item: QTableWidgetItem) -> None:
    """When a checkbox changes, update row selection accordingly."""
    table = getattr(self, "tableClients", None)
    if table is None or item is None:
        return

    if _is_sync_guarded(self):
        return

    if item.column() != 0:
        return

    row = int(item.row())
    is_checked = item.checkState() == Qt.Checked

    if is_checked:
        table.clearSelection()
        table.selectRow(row)
        if table.columnCount() > 1:
            table.setCurrentCell(row, 1)
    else:
        if table.selectionModel() and any(idx.row() == row for idx in table.selectionModel().selectedRows()):
            table.clearSelection()

    _sync_checkbox_to_selection(self)


def _extract_city(adresse: str | None) -> str:
    addr = (adresse or "").strip()
    if not addr:
        return ""
    if "," not in addr:
        return ""
    return addr.rsplit(",", 1)[-1].strip()


def _collect_filter_values(self) -> dict:
    search = (getattr(self, "editSearch", None).text() if hasattr(self, "editSearch") else "")
    combo_type = getattr(self, "comboType", None)
    combo_status = getattr(self, "comboStatus", None)

    type_text = (combo_type.currentText() if combo_type is not None else "").strip().casefold()
    status_text = (combo_status.currentText() if combo_status is not None else "").strip().casefold()

    date_start = getattr(self, "dateStart", None).date().toPyDate() if hasattr(self, "dateStart") else None
    date_end = getattr(self, "dateEnd", None).date().toPyDate() if hasattr(self, "dateEnd") else None

    return {
        "search": (search or "").strip().casefold(),
        "type": type_text,
        "status": status_text,
        "date_start": date_start,
        "date_end": date_end,
    }


def _fetch_clients_rows(session, filters: dict) -> tuple[list[dict], float]:
    allowed_types = _allowed_types_for_clients(str(filters.get("type", "") or ""))
    actif_value = _actif_filter_value(str(filters.get("status", "") or ""))

    solde_subq = (
        select(
            Document.id_tiers.label("id_tiers"),
            func.coalesce(func.sum(Document.solde), 0).label("solde"),
        )
        .where(
            Document.doc_actif == 1,
            Document.id_domaine == 1,
            Document.id_tiers.isnot(None),
        )
        .group_by(Document.id_tiers)
        .subquery()
    )

    query = (
        select(
            Tiers.id_tiers,
            Tiers.code_tiers,
            Tiers.type_tiers,
            Tiers.nom_tiers,
            Tiers.ice,
            Tiers.telephone,
            Tiers.email,
            Tiers.adresse,
            Tiers.plafond_credit,
            Tiers.actif,
            func.coalesce(solde_subq.c.solde, 0).label("solde"),
        )
        .outerjoin(solde_subq, solde_subq.c.id_tiers == Tiers.id_tiers)
        .where(Tiers.type_tiers.in_(allowed_types))
    )

    search_value = str(filters.get("search", "") or "").strip().casefold()
    if search_value:
        like = f"%{search_value}%"
        query = query.where(
            or_(
                func.lower(Tiers.code_tiers).like(like),
                func.lower(Tiers.nom_tiers).like(like),
                func.lower(func.coalesce(Tiers.ice, "")).like(like),
            )
        )

    if actif_value is not None:
        query = query.where(Tiers.actif == int(actif_value))

    date_start = filters.get("date_start")
    date_end = filters.get("date_end")
    if date_start is not None and date_end is not None:
        query = query.where(
            and_(
                func.date(Tiers.created_at) >= date_start,
                func.date(Tiers.created_at) <= date_end,
            )
        )

    query = query.order_by(Tiers.id_tiers.desc())
    results = session.execute(query).all()

    rows_data: list[dict] = []
    total_solde = 0.0

    for r in results:
        solde = float(r.solde or 0.0)
        total_solde += solde

        rows_data.append(
            {
                "id_tiers": r.id_tiers,
                "code_tiers": (r.code_tiers or "").strip(),
                "nom_tiers": (r.nom_tiers or "").strip(),
                "ice": (r.ice or "").strip() or "--",
                "telephone": (r.telephone or "").strip(),
                "email": (r.email or "").strip(),
                "ville": _extract_city(r.adresse),
                "plafond_credit": float(r.plafond_credit or 0.0),
                "solde": solde,
                "statut": "ACTIF" if int(r.actif or 0) == 1 else "INACTIF",
            }
        )

    return rows_data, total_solde


class _ClientsReloadWorker(QObject):
    finished = pyqtSignal(object, float)  # rows_data, total_solde
    failed = pyqtSignal(str)

    def __init__(self, filters: dict):
        super().__init__()
        self._filters = dict(filters or {})

    @pyqtSlot()
    def run(self) -> None:
        session = SessionLocal()
        try:
            rows_data, total_solde = _fetch_clients_rows(session, self._filters)
            self.finished.emit(rows_data, float(total_solde))
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            session.close()


def _allowed_types_for_clients(type_filter: str) -> tuple[str, ...]:
    # The UI filter is about client subtype (Entreprise / Particulier)
    # In DB we keep a single enum; treat CLIENT+SOCIETE as "Entreprise".
    if type_filter.startswith("entre"):
        return ("CLIENT", "SOCIETE")
    if type_filter.startswith("part"):
        return ("PARTICULIER",)
    return ("CLIENT", "SOCIETE", "PARTICULIER")


def _actif_filter_value(status_filter: str):
    if status_filter.startswith("act"):
        return 1
    if status_filter.startswith("ina"):
        return 0
    return None


def _set_summary_labels(self, *, total_clients: int, total_solde: float) -> None:
    if hasattr(self, "lblTotalClients"):
        self.lblTotalClients.setText(_format_int_with_spaces(total_clients))
    if hasattr(self, "lblTotalSolde"):
        self.lblTotalSolde.setText(f"{_format_amount(total_solde)} MAD")


def _set_selection_label(self, selected_count: int) -> None:
    if not hasattr(self, "lblSelection"):
        return

    if selected_count <= 0:
        self.lblSelection.setText("0 client sélectionné")
    elif selected_count == 1:
        self.lblSelection.setText("1 client sélectionné")
    else:
        self.lblSelection.setText(f"{selected_count} clients sélectionnés")


def _update_selection_label_from_table(self) -> None:
    table = getattr(self, "tableClients", None)
    if table is None:
        return

    selection_model = table.selectionModel()
    selected_rows = selection_model.selectedRows() if selection_model else []
    _set_selection_label(self, len(selected_rows))


def _on_table_selection_changed(self, _selected=None, _deselected=None) -> None:
    """Keep selection label and checkbox column in sync with current selection."""
    _update_selection_label_from_table(self)

    table = getattr(self, "tableClients", None)
    if table is not None:
        # If the user is clicking directly on the checkbox cell, avoid changing check
        # state on press before Qt toggles it on release.
        try:
            if QApplication.mouseButtons() & Qt.LeftButton:
                viewport_pos = table.viewport().mapFromGlobal(QCursor.pos())
                row = table.rowAt(viewport_pos.y())
                col = table.columnAt(viewport_pos.x())
                if int(col) == 0 and int(row) >= 0:
                    return
        except Exception:
            pass

    _sync_checkbox_to_selection(self)


def _render_rows(self, rows_data: list[dict]) -> None:
    table = getattr(self, "tableClients", None)
    if table is None:
        return

    # Reset sync state because row indices may change on reload/sort.
    setattr(self, "_clients_checkbox_synced_item", None)

    was_sorting_enabled = table.isSortingEnabled()
    table.setUpdatesEnabled(False)
    table.blockSignals(True)
    try:
        if was_sorting_enabled:
            table.setSortingEnabled(False)

        table.setRowCount(len(rows_data))

        for row_idx, row in enumerate(rows_data):
            values = [
                None,  # checkbox
                row.get("code_tiers", ""),
                row.get("nom_tiers", ""),
                row.get("ice", "--"),
                row.get("telephone", ""),
                row.get("email", ""),
                row.get("ville", ""),
                row.get("plafond_credit", 0.0),
                row.get("solde", 0.0),
                row.get("statut", ""),
                row.get("id_tiers", ""),
            ]

            for col_idx, value in enumerate(values):
                if col_idx == 0:
                    item = _build_checkbox_item(False)
                elif col_idx in (7, 8):
                    item = _build_table_item(value, align_right=True, numeric=True)
                else:
                    item = _build_table_item(value)
                table.setItem(row_idx, col_idx, item)
    finally:
        if was_sorting_enabled:
            table.setSortingEnabled(True)
        table.blockSignals(False)
        table.setUpdatesEnabled(True)

    _update_selection_label_from_table(self)
    _sync_checkbox_to_selection(self)


@with_db_session
def _reload_table_and_totals(self, session=None) -> None:
    rows_data, total_solde = _fetch_clients_rows(session, _collect_filter_values(self))
    _render_rows(self, rows_data)
    _set_summary_labels(self, total_clients=len(rows_data), total_solde=float(total_solde))


def _request_reload_async(self, *, filters: dict | None = None) -> None:
    """Run the reload query in a background thread to avoid blocking the UI."""
    if filters is None:
        filters = _collect_filter_values(self)

    if getattr(self, "_clients_reload_in_progress", False):
        setattr(self, "_clients_reload_pending_filters", dict(filters))
        return

    setattr(self, "_clients_reload_in_progress", True)
    setattr(self, "_clients_reload_pending_filters", None)

    _set_loading_state(self, True)

    thread = QThread(self)
    worker = _ClientsReloadWorker(filters)
    worker.moveToThread(thread)

    def _finish(rows_data: list[dict], total_solde: float) -> None:
        _set_loading_state(self, False)
        try:
            _render_rows(self, rows_data)
            _set_summary_labels(self, total_clients=len(rows_data), total_solde=float(total_solde))
        except RuntimeError:
            return
        finally:
            setattr(self, "_clients_reload_in_progress", False)

        pending = getattr(self, "_clients_reload_pending_filters", None)
        if pending is not None:
            setattr(self, "_clients_reload_pending_filters", None)
            _request_reload_async(self, filters=pending)

    def _fail(message: str) -> None:
        _set_loading_state(self, False)
        setattr(self, "_clients_reload_in_progress", False)
        try:
            MessageBox(
                variant="attention",
                title="Clients",
                message=f"Erreur lors du chargement des clients: {message}",
                parent=self,
            ).exec_()
        except RuntimeError:
            return
        finally:
            pending = getattr(self, "_clients_reload_pending_filters", None)
            if pending is not None:
                setattr(self, "_clients_reload_pending_filters", None)
                _request_reload_async(self, filters=pending)

    thread.started.connect(worker.run)
    worker.finished.connect(_finish, Qt.QueuedConnection)
    worker.failed.connect(_fail, Qt.QueuedConnection)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    worker.failed.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    setattr(self, "_clients_reload_thread", thread)
    setattr(self, "_clients_reload_worker", worker)
    thread.start()


def _get_selected_tiers_id(self):
    table = getattr(self, "tableClients", None)
    if table is None:
        return None

    selection_model = table.selectionModel()
    selected_rows = selection_model.selectedRows() if selection_model else []
    if not selected_rows:
        return None

    row_idx = selected_rows[0].row()
    id_item = table.item(row_idx, 10)
    if not id_item:
        return None

    raw = (id_item.text() or "").strip()
    if not raw:
        return None

    try:
        return int(raw)
    except ValueError:
        return None


def _on_filter_clicked(self) -> None:
    _request_reload_async(self)


def _on_export_excel_clicked(self) -> None:
    table = getattr(self, "tableClients", None)
    if table is None:
        return

    default_name = f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path, _ = QFileDialog.getSaveFileName(self, "Exporter", default_name, "CSV (*.csv)")
    if not file_path:
        return

    try:
        headers = []
        # Export visible columns (1..9)
        for col in range(1, 10):
            item = table.horizontalHeaderItem(col)
            headers.append((item.text() if item else "").strip())

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
            for row in range(table.rowCount()):
                writer.writerow(
                    [
                        (table.item(row, col).text() if table.item(row, col) else "")
                        for col in range(1, 10)
                    ]
                )

        MessageBox(variant="info", title="Export", message="Export terminé.", parent=self).exec_()
    except Exception as exc:
        MessageBox(variant="attention", title="Export", message=f"Erreur export: {exc}", parent=self).exec_()


def _on_nouveau_clicked(self) -> None:
    parent_window = self.window() if hasattr(self, "window") else None
    dialog = NouveauClientWindow(parent=parent_window)
    dialog.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        _request_reload_async(self)


def _on_modifier_clicked(self) -> None:
    tiers_id = _get_selected_tiers_id(self)
    if not tiers_id:
        MessageBox(variant="info", title="Modifier", message="Veuillez sélectionner un client à modifier.", parent=self).exec_()
        return

    parent_window = self.window() if hasattr(self, "window") else None
    dialog = NouveauClientWindow(parent=parent_window, tiers_id=tiers_id)
    dialog.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        _request_reload_async(self)


@with_db_session
def _on_supprimer_clicked(self, session=None) -> None:
    tiers_id = _get_selected_tiers_id(self)
    if not tiers_id:
        MessageBox(variant="info", title="Supprimer", message="Veuillez sélectionner un client à supprimer.", parent=self).exec_()
        return

    table = getattr(self, "tableClients", None)
    name_item = table.item(table.currentRow(), 2) if table is not None else None
    name = (name_item.text() if name_item else "").strip() or f"ID {tiers_id}"

    answer = MessageBox(
        variant="question",
        title="Confirmation",
        message=f"Désactiver le client {name} ?",
        parent=self,
    ).exec_()

    if answer != QDialog.Accepted:
        return

    tiers = session.execute(select(Tiers).where(Tiers.id_tiers == int(tiers_id))).scalar_one_or_none()
    if not tiers:
        _reload_table_and_totals(self)
        return

    old_values = {
        "code_tiers": (tiers.code_tiers or "").strip() or None,
        "nom_tiers": (tiers.nom_tiers or "").strip() or None,
        "type_tiers": (tiers.type_tiers or "").strip() or None,
        "actif": int(tiers.actif or 0),
    }

    tiers.actif = 0
    session.flush()
    log_audit_event(
        session,
        table_name=Tiers.__tablename__,
        record_id=int(tiers.id_tiers),
        action="DELETE",
        old_values=old_values,
        new_values={"actif": 0},
        comment=f"Désactivation client: {(tiers.code_tiers or '').strip()} {(tiers.nom_tiers or '').strip()}".strip(),
    )
    session.commit()
    _request_reload_async(self)


def _show_table_context_menu(self, pos) -> None:
    table = getattr(self, "tableClients", None)
    if table is None:
        return

    index = table.indexAt(pos)
    if index.isValid():
        table.selectRow(index.row())

    menu = QMenu(table)
    apply_menu_style(menu)
    action_edit = menu.addAction("Modifier")
    action_delete = menu.addAction("Supprimer")

    chosen = menu.exec_(table.viewport().mapToGlobal(pos))
    if chosen == action_edit:
        _on_modifier_clicked(self)
    elif chosen == action_delete:
        _on_supprimer_clicked(self)


def _connect_signals(self) -> None:
    if hasattr(self, "btnFilter"):
        self.btnFilter.clicked.connect(lambda: _on_filter_clicked(self))

    if hasattr(self, "tbNew"):
        self.tbNew.clicked.connect(lambda: _on_nouveau_clicked(self))
    if hasattr(self, "tbEdit"):
        self.tbEdit.clicked.connect(lambda: _on_modifier_clicked(self))
    if hasattr(self, "tbDelete"):
        self.tbDelete.clicked.connect(lambda: _on_supprimer_clicked(self))
    if hasattr(self, "tbExportExcel"):
        self.tbExportExcel.clicked.connect(lambda: _on_export_excel_clicked(self))
    if hasattr(self, "tbDuplicate"):
        self.tbDuplicate.clicked.connect(lambda: _on_filter_clicked(self))

    for name in ("editSearch",):
        line = getattr(self, name, None)
        if line is None:
            continue
        try:
            line.returnPressed.disconnect()
        except TypeError:
            pass
        line.returnPressed.connect(lambda: _request_reload_async(self))

    for combo_name in ("comboType", "comboStatus"):
        combo = getattr(self, combo_name, None)
        if combo is None:
            continue
        try:
            combo.activated.disconnect()
        except TypeError:
            pass
        combo.activated.connect(lambda _idx: _request_reload_async(self))

    table = getattr(self, "tableClients", None)
    if table is not None:
        # Always keep selection as a single row, even when clicking on checkboxes.
        try:
            table.cellPressed.disconnect()
        except TypeError:
            pass
        table.cellPressed.connect(lambda row, _col: (table.clearSelection(), table.selectRow(row), table.setCurrentCell(row, 1)))

        # Sync checkbox column <-> selection like liste ventes.
        try:
            table.itemChanged.disconnect()
        except TypeError:
            pass
        table.itemChanged.connect(lambda item: _on_table_item_changed(self, item))

        try:
            table.cellClicked.disconnect()
        except TypeError:
            pass
        table.cellClicked.connect(lambda _row, _col: _sync_checkbox_to_selection(self))

        try:
            table.itemDoubleClicked.disconnect()
        except TypeError:
            pass
        table.itemDoubleClicked.connect(lambda _item: _on_modifier_clicked(self))

        table.setContextMenuPolicy(Qt.CustomContextMenu)
        try:
            table.customContextMenuRequested.disconnect()
        except TypeError:
            pass
        table.customContextMenuRequested.connect(lambda pos: _show_table_context_menu(self, pos))

        # Update selection label when selection changes
        try:
            table.selectionModel().selectionChanged.disconnect()
        except Exception:
            pass
        table.selectionModel().selectionChanged.connect(
            lambda sel, desel: _on_table_selection_changed(self, sel, desel)
        )


def liste_clients_setup(self) -> None:
    _request_reload_async(self)
    _connect_signals(self)
