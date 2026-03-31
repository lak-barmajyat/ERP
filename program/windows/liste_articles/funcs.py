import csv
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMenu, QTableWidgetItem

from program.services import Article, Famille, MessageBox, and_, func, select, with_db_session
from program.windows.nouveau_article import NouveauArticleWindow


class _NumericSortTableWidgetItem(QTableWidgetItem):
    """Sort using hidden numeric value while keeping original display text."""

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
    return f"{_safe_float(value):,.2f}"


def _build_table_item(value, *, align_right: bool = False, numeric: bool = False):
    if numeric:
        display_text = _format_number(value)
        item = _NumericSortTableWidgetItem(display_text)
        item.setData(Qt.UserRole, _safe_float(value))
    else:
        item = QTableWidgetItem(str(value if value is not None else ""))

    item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if align_right else Qt.AlignLeft))
    return item


@with_db_session
def _setup_famille_filter_items(self, session=None):
    combo = getattr(self, "comboDocType", None)
    if combo is None:
        return

    current_data = combo.currentData() if combo.count() else None

    combo.blockSignals(True)
    try:
        combo.clear()
        combo.addItem("Toutes les familles", None)

        familles = session.execute(
            select(Famille.id_famille, Famille.nom_famille).order_by(Famille.nom_famille)
        ).all()
        for fam_id, fam_name in familles:
            label = (fam_name or "").strip() or f"Famille {fam_id}"
            combo.addItem(label, int(fam_id) if fam_id is not None else None)

        if current_data is not None:
            for idx in range(combo.count()):
                if combo.itemData(idx) == current_data:
                    combo.setCurrentIndex(idx)
                    break
    finally:
        combo.blockSignals(False)


def _collect_filter_values(self):
    reference = (getattr(self, "editcodeclient", None).text() if hasattr(self, "editcodeclient") else "")
    nom_article = (getattr(self, "editClient", None).text() if hasattr(self, "editClient") else "")

    combo = getattr(self, "comboDocType", None)
    famille_id = combo.currentData() if combo is not None else None

    return {
        "reference": (reference or "").strip().casefold(),
        "nom_article": (nom_article or "").strip().casefold(),
        "famille_id": famille_id,
    }


def _clear_filters(self):
    if hasattr(self, "editcodeclient"):
        self.editcodeclient.clear()
    if hasattr(self, "editClient"):
        self.editClient.clear()
    if hasattr(self, "comboDocType"):
        self.comboDocType.setCurrentIndex(0)


def _set_summary_labels(self, *, nb_articles: int, under_minimum: int):
    if hasattr(self, "labelNbDocumentsValue"):
        self.labelNbDocumentsValue.setText(str(nb_articles))
    if hasattr(self, "labelTotalHtValue"):
        self.labelTotalHtValue.setText(str(under_minimum))


def _render_rows(self, rows_data):
    if not hasattr(self, "tableDocuments"):
        return

    was_sorting_enabled = self.tableDocuments.isSortingEnabled()
    if was_sorting_enabled:
        self.tableDocuments.setSortingEnabled(False)

    self.tableDocuments.setRowCount(len(rows_data))

    for row_idx, row in enumerate(rows_data):
        values = [
            row.get("reference_interne", ""),
            row.get("nom_article", ""),
            row.get("famille", ""),
            row.get("prix_vente_ht", 0),
            row.get("prix_achat_ht", 0),
            row.get("taux_tva", 0),
            row.get("quantite", 0),
            row.get("id_article", ""),
        ]

        for col_idx, value in enumerate(values):
            is_numeric = col_idx in (3, 4, 5, 6)
            item = _build_table_item(value, align_right=is_numeric, numeric=is_numeric)
            self.tableDocuments.setItem(row_idx, col_idx, item)

    if was_sorting_enabled:
        self.tableDocuments.setSortingEnabled(True)


@with_db_session
def _reload_table_total_labels(self, session=None):
    filters = _collect_filter_values(self)

    query = (
        select(
            Article.id_article,
            Article.reference_interne,
            Article.nom_article,
            Article.prix_vente_ht,
            Article.prix_achat_ht,
            Article.taux_tva,
            Article.quantite,
            Article.quantite_min,
            Famille.id_famille,
            Famille.nom_famille,
        )
        .outerjoin(Famille, Article.id_famille == Famille.id_famille)
        .where(Article.actif == 1)
    )

    if filters["reference"]:
        query = query.where(func.lower(Article.reference_interne).like(f"%{filters['reference']}%"))
    if filters["nom_article"]:
        query = query.where(func.lower(Article.nom_article).like(f"%{filters['nom_article']}%"))
    if filters["famille_id"]:
        query = query.where(and_(Article.id_famille == int(filters["famille_id"])))

    query = query.order_by(Article.id_article.desc())

    results = session.execute(query).all()

    rows_data = []
    under_minimum = 0

    for r in results:
        fam_id = r.id_famille
        fam_name = (r.nom_famille or "").strip()
        famille_display = ""
        if fam_id is not None and fam_name:
            famille_display = f"{int(fam_id)} - {fam_name}"
        elif fam_id is not None:
            famille_display = str(int(fam_id))
        elif fam_name:
            famille_display = fam_name

        quantite = float(r.quantite or 0)
        quantite_min = r.quantite_min
        if quantite_min is not None and quantite < float(quantite_min):
            under_minimum += 1

        rows_data.append(
            {
                "id_article": r.id_article,
                "reference_interne": r.reference_interne or "",
                "nom_article": r.nom_article or "",
                "famille": famille_display,
                "prix_vente_ht": float(r.prix_vente_ht or 0),
                "prix_achat_ht": float(r.prix_achat_ht or 0),
                "taux_tva": float(r.taux_tva or 0),
                "quantite": quantite,
            }
        )

    _render_rows(self, rows_data)
    _set_summary_labels(self, nb_articles=len(rows_data), under_minimum=under_minimum)


def _connect_filter_enter_reload(self):
    for name in ("editcodeclient", "editClient"):
        line = getattr(self, name, None)
        if line is None:
            continue
        try:
            line.returnPressed.disconnect()
        except TypeError:
            pass
        line.returnPressed.connect(lambda: _reload_table_total_labels(self))

    combo = getattr(self, "comboDocType", None)
    if combo is not None:
        try:
            combo.activated.disconnect()
        except TypeError:
            pass
        combo.activated.connect(lambda _idx: _reload_table_total_labels(self))


def _get_selected_article_id(self):
    if not hasattr(self, "tableDocuments"):
        return None

    selection_model = self.tableDocuments.selectionModel()
    selected_rows = selection_model.selectedRows() if selection_model else []
    if not selected_rows:
        return None

    row_idx = selected_rows[0].row()
    id_item = self.tableDocuments.item(row_idx, 7)
    if not id_item:
        return None

    raw = (id_item.text() or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _on_filter_clicked(self):
    _reload_table_total_labels(self)


def _on_clear_filters_clicked(self):
    _clear_filters(self)
    _reload_table_total_labels(self)


def _on_export_excel_clicked(self):
    if not hasattr(self, "tableDocuments"):
        return

    default_name = f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Exporter",
        default_name,
        "CSV (*.csv)",
    )
    if not file_path:
        return

    try:
        headers = []
        for col in range(0, 7):
            item = self.tableDocuments.horizontalHeaderItem(col)
            headers.append((item.text() if item else "").strip())

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
            for row in range(self.tableDocuments.rowCount()):
                writer.writerow(
                    [
                        (self.tableDocuments.item(row, col).text() if self.tableDocuments.item(row, col) else "")
                        for col in range(0, 7)
                    ]
                )

        MessageBox(
            variant="info",
            title="Export",
            message="Export terminé.",
            parent=self,
        ).exec_()
    except Exception as exc:
        MessageBox(
            variant="attention",
            title="Export",
            message=f"Erreur export: {exc}",
            parent=self,
        ).exec_()


def _on_nouveau_clicked(self):
    parent_window = self.window() if hasattr(self, "window") else None
    dialog = NouveauArticleWindow(parent=parent_window)
    dialog.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        _reload_table_total_labels(self)


def _on_modifier_clicked(self):
    article_id = _get_selected_article_id(self)
    if not article_id:
        MessageBox(
            variant="info",
            title="Modifier",
            message="Veuillez sélectionner un article à modifier.",
            parent=self,
        ).exec_()
        return

    parent_window = self.window() if hasattr(self, "window") else None
    dialog = NouveauArticleWindow(parent=parent_window, article_id=article_id)
    dialog.setWindowModality(Qt.WindowModal if parent_window else Qt.ApplicationModal)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        _reload_table_total_labels(self)


@with_db_session
def _on_supprimer_clicked(self, session=None):
    article_id = _get_selected_article_id(self)
    if not article_id:
        MessageBox(
            variant="info",
            title="Supprimer",
            message="Veuillez sélectionner un article à supprimer.",
            parent=self,
        ).exec_()
        return

    ref_item = self.tableDocuments.item(self.tableDocuments.currentRow(), 0) if hasattr(self, "tableDocuments") else None
    ref = (ref_item.text() if ref_item else "").strip() or f"ID {article_id}"

    answer = MessageBox(
        variant="question",
        title="Confirmation",
        message=f"Supprimer l'article {ref} ?",
        parent=self,
    ).exec_()

    if answer != QDialog.Accepted:
        return

    article = session.execute(select(Article).where(Article.id_article == int(article_id))).scalar_one_or_none()
    if not article or int(article.actif or 0) == 0:
        _reload_table_total_labels(self)
        return

    article.actif = 0
    _reload_table_total_labels(self)


def _connect_signals(self):
    if hasattr(self, "btnFilter"):
        self.btnFilter.clicked.connect(lambda: _on_filter_clicked(self))

    if hasattr(self, "btnClearFilters"):
        self.btnClearFilters.clicked.connect(lambda: _on_clear_filters_clicked(self))

    _connect_filter_enter_reload(self)

    if hasattr(self, "tbNew"):
        self.tbNew.clicked.connect(lambda: _on_nouveau_clicked(self))
    if hasattr(self, "tbEdit"):
        self.tbEdit.clicked.connect(lambda: _on_modifier_clicked(self))
    if hasattr(self, "tbDelete"):
        self.tbDelete.clicked.connect(lambda: _on_supprimer_clicked(self))
    if hasattr(self, "tbExportExcel"):
        self.tbExportExcel.clicked.connect(lambda: _on_export_excel_clicked(self))

    table = getattr(self, "tableDocuments", None)
    if table is not None:
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


def _show_table_context_menu(self, pos) -> None:
    table = getattr(self, "tableDocuments", None)
    if table is None:
        return

    index = table.indexAt(pos)
    if index.isValid():
        table.selectRow(index.row())

    menu = QMenu(table)
    action_edit = menu.addAction("Modifier")
    action_delete = menu.addAction("Supprimer")

    chosen = menu.exec_(table.viewport().mapToGlobal(pos))
    if chosen == action_edit:
        _on_modifier_clicked(self)
    elif chosen == action_delete:
        _on_supprimer_clicked(self)


def liste_articles_setup(self):
    _setup_famille_filter_items(self)
    _reload_table_total_labels(self)
    _connect_signals(self)
