import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Import your project's DB helpers and models
from program.services import with_db_session, select, Document, RefTypeDocument, Tiers, RefStatutDocument
from test import GenericDocumentTableWidget


@with_db_session
def fetch_real_documents(session=None):
    """Fetch documents for domain_id = 1 (Sales) with all related names."""
    docs = session.execute(
        select(Document).where(Document.id_domaine == 1).order_by(Document.id_document.desc())
    ).scalars().all()

    # Prefetch reference dictionaries
    type_dict = {t.id_type_document: t.libelle_type for t in session.execute(select(RefTypeDocument)).scalars()}
    client_dict = {t.id_tiers: t.nom_tiers for t in session.execute(select(Tiers)).scalars()}
    code_dict = {t.id_tiers: t.code_tiers or "" for t in session.execute(select(Tiers)).scalars()}
    status_dict = {s.id_statut: s.libelle_statut for s in session.execute(select(RefStatutDocument)).scalars()}

    rows = []
    for doc in docs:
        rows.append({
            "type": type_dict.get(doc.id_type_document, "N/A"),
            "doc_number": doc.numero_document,
            "date": doc.date_document.strftime("%Y-%m-%d"),
            "client": client_dict.get(doc.id_tiers, "N/A"),
            "code_client": code_dict.get(doc.id_tiers, ""),
            "total_ht": doc.total_ht,
            "total_ttc": doc.total_ttc,
            "solde": doc.solde,
            "status": status_dict.get(doc.id_statut, "N/A"),
            "id_document": doc.id_document,
        })
    return rows


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Generic Table with Real Data")
        self.resize(1200, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table_widget = GenericDocumentTableWidget()
        layout.addWidget(self.table_widget)

        # Define columns (visible headers and corresponding dict keys)
        self.table_widget.set_columns(
            headers=["Type", "N° Document", "Date", "Client", "Total HT", "Total TTC", "Solde", "Statut"],
            keys=["type", "doc_number", "date", "client", "total_ht", "total_ttc", "solde", "status"]
        )

        # Custom context menu actions
        self.table_widget.add_context_menu_action("Afficher détails", self.on_show_details)
        self.table_widget.add_context_menu_action("Supprimer (demo)", self.on_demo_delete)

        # Double‑click action
        self.table_widget.rowDoubleClicked.connect(self.on_double_click)

        # Load real data
        data = fetch_real_documents()
        self.table_widget.set_data(data)

    def on_show_details(self, row_data):
        print(f"Details for {row_data.get('doc_number')}: {row_data}")

    def on_demo_delete(self, row_data):
        print(f"Delete requested for {row_data.get('doc_number')} (demo only)")

    def on_double_click(self, row, row_data):
        print(f"Double-click on row {row}: {row_data.get('doc_number')} - {row_data.get('client')}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TestWindow()
    win.show()
    sys.exit(app.exec_())