from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QTableWidgetItem, QWidget

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


def _fmt_amount(value) -> str:
    try:
        return f"{float(value or 0):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _fmt_qty(value) -> str:
    try:
        qty = float(value or 0)
    except (TypeError, ValueError):
        return "0"
    return f"{qty:g}"


def _checkbox_cell(checked=True):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignCenter)
    checkbox = QCheckBox(container)
    checkbox.setChecked(bool(checked))
    layout.addWidget(checkbox)
    return container


def _configure_table(self):
    if not hasattr(self, "tableTransferDetails"):
        return

    self.tableTransferDetails.setColumnCount(6)
    self.tableTransferDetails.setHorizontalHeaderLabels([
        "",
        "Référence",
        "Désignation",
        "Qté",
        "Prix unitaire",
        "Total HT",
    ])

    header = self.tableTransferDetails.horizontalHeader()
    header.setStretchLastSection(False)
    header.setSectionResizeMode(0, header.Fixed)
    header.setSectionResizeMode(1, header.ResizeToContents)
    header.setSectionResizeMode(2, header.Stretch)
    header.setSectionResizeMode(3, header.ResizeToContents)
    header.setSectionResizeMode(4, header.ResizeToContents)
    header.setSectionResizeMode(5, header.ResizeToContents)
    self.tableTransferDetails.setColumnWidth(0, 38)


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
        # Placeholder: accept for now until transfer workflow is implemented.
        self.btnLaunchTransfer.clicked.connect(self.accept)

    if hasattr(self, "checkSelectAll"):
        try:
            self.checkSelectAll.toggled.disconnect()
        except TypeError:
            pass
        self.checkSelectAll.toggled.connect(lambda checked: _toggle_all_rows(self, checked))

    if hasattr(self, "comboToType"):
        try:
            self.comboToType.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.comboToType.currentIndexChanged.connect(lambda _: _refresh_target_code(self))


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


def _refresh_target_code(self):
    if not hasattr(self, "comboToType") or not hasattr(self, "CodeEditLine"):
        return

    code_type = (self.comboToType.currentData() or "").strip()
    if not code_type:
        self.CodeEditLine.clear()
        return

    try:
        self.CodeEditLine.setText(generate_document_number(code_type))
    except Exception:
        self.CodeEditLine.clear()


def _populate_target_types(self, target_types):
    if not hasattr(self, "comboToType"):
        return

    self.comboToType.blockSignals(True)
    self.comboToType.clear()
    for code_type, libelle in target_types:
        label = f"{libelle} ({code_type})" if libelle else code_type
        self.comboToType.addItem(label, code_type)
    self.comboToType.blockSignals(False)

    if hasattr(self, "CodeEditLine"):
        self.CodeEditLine.setReadOnly(True)

    _refresh_target_code(self)


def _populate_details_table(self, detail_rows):
    if not hasattr(self, "tableTransferDetails"):
        return

    self.tableTransferDetails.setRowCount(0)

    for detail, article_ref, article_desc in detail_rows:
        row = self.tableTransferDetails.rowCount()
        self.tableTransferDetails.insertRow(row)

        self.tableTransferDetails.setCellWidget(row, 0, _checkbox_cell(True))

        designation = (detail.description or "").strip() or (article_desc or "")
        row_values = [
            article_ref or "",
            designation,
            _fmt_qty(detail.quantite),
            _fmt_amount(detail.prix_unitaire_ht),
            _fmt_amount(detail.total_ligne_ht),
        ]

        for col, value in enumerate(row_values, start=1):
            item = QTableWidgetItem(str(value))
            if col in (3, 4, 5):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableTransferDetails.setItem(row, col, item)


@with_db_session
def _load_source_document(self, source_doc_id, source_doc_number=None, session=None):
    source_row = session.execute(
        select(
            Document,
            RefTypeDocument.code_type,
            RefTypeDocument.libelle_type,
            RefTypeDocument.id_domaine,
            Tiers.nom_tiers,
        )
        .join(RefTypeDocument, Document.id_type_document == RefTypeDocument.id_type_document)
        .outerjoin(Tiers, Document.id_tiers == Tiers.id_tiers)
        .where(Document.id_document == source_doc_id)
    ).one_or_none()

    if not source_row:
        MessageBox(
            variant="error",
            title="Transformer",
            message="Document source introuvable.",
            parent=self,
        ).exec_()
        return

    document = source_row[0]
    source_type_code = source_row[1] or ""
    source_type_label = source_row[2] or "N/A"
    source_domain_id = source_row[3]
    source_client_name = source_row[4] or "N/A"

    doc_number = source_doc_number or document.numero_document or "N/A"

    if hasattr(self, "labelDocCode"):
        self.labelDocCode.setText(doc_number)
    if hasattr(self, "labelSourceDocValue"):
        self.labelSourceDocValue.setText(doc_number)
    if hasattr(self, "labelSourceTypeValue"):
        self.labelSourceTypeValue.setText(source_type_label)
    if hasattr(self, "labelSourceClientValue"):
        self.labelSourceClientValue.setText(source_client_name)
    if hasattr(self, "labelSourceTotalValue"):
        self.labelSourceTotalValue.setText(f"{_fmt_amount(document.total_ttc)} MAD")

    detail_rows = session.execute(
        select(DetailDocument, Article.reference_interne, Article.description)
        .join(Article, DetailDocument.id_article == Article.id_article)
        .where(DetailDocument.id_document == source_doc_id)
        .order_by(DetailDocument.id_detail)
    ).all()
    _populate_details_table(self, detail_rows)

    target_types = session.execute(
        select(RefTypeDocument.code_type, RefTypeDocument.libelle_type)
        .where(
            and_(
                RefTypeDocument.id_domaine == source_domain_id,
                RefTypeDocument.actif == 1,
                RefTypeDocument.code_type != source_type_code,
            )
        )
        .order_by(RefTypeDocument.ordre, RefTypeDocument.libelle_type)
    ).all()
    _populate_target_types(self, target_types)


def transfer_window_setup(self, source_doc_id=None, source_doc_number=None):
    """Initialize transfer dialog and load source-document data into the form."""
    _configure_table(self)
    _connect_signals(self)

    if source_doc_id is not None:
        self.source_document_id = int(source_doc_id)
        _load_source_document(
            self,
            source_doc_id=int(source_doc_id),
            source_doc_number=source_doc_number,
        )
        return

    # Keep labels consistent when no source document is provided.
    if source_doc_number:
        if hasattr(self, "labelDocCode"):
            self.labelDocCode.setText(str(source_doc_number))
        if hasattr(self, "labelSourceDocValue"):
            self.labelSourceDocValue.setText(str(source_doc_number))
