import json
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from program.services import AuditLog, MessageBox, Utilisateur, func, select, with_db_session
from program.themes import shared_input_popup_style as style


class HistoriqueWindow(QDialog):
    """Full audit history window with a searchable table."""

    _SEARCH_ROLE = int(Qt.UserRole) + 1

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Historique")
        self.setMinimumSize(1100, 650)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        title = QLabel("Historique")
        title.setObjectName("historyTitle")
        root_layout.addWidget(title)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        label_search = QLabel("Rechercher")
        top_row.addWidget(label_search)

        self.editSearch = QLineEdit()
        self.editSearch.setObjectName("editSearch")
        self.editSearch.setPlaceholderText(
            "Rechercher (utilisateur, action, table, id, IP, commentaire...)"
        )
        top_row.addWidget(self.editSearch, 1)

        self.btnClose = QPushButton("Fermer")
        self.btnClose.setObjectName("btnClose")
        self.btnClose.clicked.connect(self.close)
        top_row.addWidget(self.btnClose)

        root_layout.addLayout(top_row)

        self.tableHistorique = QTableWidget()
        self.tableHistorique.setObjectName("tableHistorique")
        self.tableHistorique.setColumnCount(7)
        self.tableHistorique.setHorizontalHeaderLabels(
            [
                "Date",
                "Heure",
                "Utilisateur",
                "Action",
                "Commentaire",
                "Anciennes valeurs",
                "Nouvelles valeurs",
            ]
        )

        self.tableHistorique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableHistorique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableHistorique.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableHistorique.setAlternatingRowColors(True)
        self.tableHistorique.setShowGrid(False)
        self.tableHistorique.verticalHeader().setVisible(False)

        header = self.tableHistorique.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Heure
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Utilisateur
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Action
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Commentaire
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Anciennes valeurs
        header.setSectionResizeMode(6, QHeaderView.Stretch)           # Nouvelles valeurs

        root_layout.addWidget(self.tableHistorique, 1)

        style.apply_input_styles_to_window(
            self,
            row_height=36,
            widget_styles_map={
                "btnClose": ["QPushButton", "primary"],
            },
        )
        self._apply_table_style()

        self.editSearch.textChanged.connect(self._apply_search_filter)

        self._load_history_safe()

    def _apply_table_style(self) -> None:
        qss = f"""
QTableWidget#tableHistorique {{
    background-color: {style.COLOR_BG};
    border: {style.BORDER_SIZE}px solid {style.COLOR_BORDER};
    border-radius: {style.RADIUS_INPUT}px;
    gridline-color: transparent;
    outline: 0;
    color: {style.COLOR_TEXT};
}}

QTableWidget#tableHistorique::item {{
    padding: {style.ITEM_PADDING_Y}px {style.ITEM_PADDING_X}px;
    border-bottom: {style.BORDER_SIZE}px solid {style.COLOR_BG_SOFT};
}}

QTableWidget#tableHistorique::item:selected {{
    background-color: {style.COLOR_ITEM_SELECTED_BG};
    color: {style.COLOR_TEXT};
}}

QTableWidget#tableHistorique::item:hover {{
    background-color: {style.COLOR_ITEM_HOVER_BG};
}}

QTableWidget#tableHistorique QHeaderView::section {{
    background-color: {style.COLOR_BG_SOFT};
    color: {style.COLOR_TEXT};
    font: {style.MENU_FONT_WEIGHT} {style.MENU_FONT_SIZE_PT}pt \"{style.FONT_FAMILY}\";
    padding: 8px 10px;
    border: none;
    border-bottom: {style.BORDER_SIZE}px solid {style.COLOR_BORDER};
    border-right: {style.BORDER_SIZE}px solid {style.COLOR_BORDER};
}}

QTableWidget#tableHistorique QHeaderView::section:last {{
    border-right: none;
}}
"""
        self.tableHistorique.setStyleSheet(qss)

    @staticmethod
    def _format_date(value: datetime | None) -> str:
        if value is None:
            return ""
        try:
            return value.strftime("%d/%m/%Y")
        except Exception:
            return str(value)

    @staticmethod
    def _format_time(value: datetime | None) -> str:
        if value is None:
            return ""
        try:
            return value.strftime("%H:%M")
        except Exception:
            return str(value)

    @staticmethod
    def _json_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, ensure_ascii=False, sort_keys=True)
            except Exception:
                return str(value)
        return str(value)

    def _load_history_safe(self) -> None:
        try:
            self._load_history()
        except Exception as exc:
            MessageBox(
                variant="attention",
                title="Historique",
                message=f"Impossible de charger l'historique.\n\n{exc}",
                parent=self,
            ).exec_()

    @with_db_session
    def _load_history(self, session=None) -> None:
        query = (
            select(
                AuditLog.id_audit,
                AuditLog.date_action,
                AuditLog.id_utilisateur,
                Utilisateur.nom_utilisateur,
                AuditLog.action,
                AuditLog.table_name,
                AuditLog.record_id,
                AuditLog.ip_client,
                AuditLog.commentaire,
                AuditLog.old_values_json,
                AuditLog.new_values_json,
            )
            .outerjoin(Utilisateur, AuditLog.id_utilisateur == Utilisateur.id_utilisateur)
            .order_by(AuditLog.id_audit.desc())
        )

        rows = session.execute(query).all()

        self.tableHistorique.setSortingEnabled(False)
        self.tableHistorique.blockSignals(True)
        try:
            self.tableHistorique.setRowCount(0)

            for (
                audit_id,
                date_action,
                user_id,
                username,
                action,
                table_name,
                record_id,
                ip_client,
                commentaire,
                old_json,
                new_json,
            ) in rows:
                user_label = (username or "").strip() or (
                    f"Utilisateur {int(user_id)}" if user_id is not None else "Système"
                )

                values = [
                    self._format_date(date_action),
                    self._format_time(date_action),
                    user_label,
                    (action or "").strip(),
                    (commentaire or "").strip(),
                    self._json_text(old_json),
                    self._json_text(new_json),
                ]

                row_index = self.tableHistorique.rowCount()
                self.tableHistorique.insertRow(row_index)

                extra_tokens = [
                    str(audit_id or ""),
                    "" if user_id is None else str(int(user_id)),
                    (table_name or "").strip(),
                    (record_id or "").strip(),
                    (ip_client or "").strip(),
                ]
                search_blob = " ".join([*values, *extra_tokens]).casefold()

                for col, text in enumerate(values):
                    item = QTableWidgetItem(text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

                    if col in {4, 5, 6} and text:
                        item.setToolTip(text)

                    if col == 0:
                        item.setData(self._SEARCH_ROLE, search_blob)

                    self.tableHistorique.setItem(row_index, col, item)

        finally:
            self.tableHistorique.blockSignals(False)
            self.tableHistorique.setSortingEnabled(True)

        self._apply_search_filter(self.editSearch.text())

    def _apply_search_filter(self, text: str) -> None:
        needle = (text or "").strip().casefold()
        if not needle:
            for row in range(self.tableHistorique.rowCount()):
                self.tableHistorique.setRowHidden(row, False)
            return

        for row in range(self.tableHistorique.rowCount()):
            id_item = self.tableHistorique.item(row, 0)
            blob = ""
            if id_item is not None:
                try:
                    blob = str(id_item.data(self._SEARCH_ROLE) or "")
                except Exception:
                    blob = ""
            self.tableHistorique.setRowHidden(row, needle not in blob)
