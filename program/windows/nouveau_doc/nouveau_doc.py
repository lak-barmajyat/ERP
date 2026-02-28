import os
import sys

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QLineEdit

from program.services import generate_document_number, with_db_session, select, Tiers
from program.widgetstyles.lineedit_combo_style import LineEditAutoComplete
from .select_doc_type import SelectDocTypeDialog


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class NouveauDocWindow(QMainWindow):
    def __init__(self):
        super(NouveauDocWindow, self).__init__()
        loadUi(resource_path("nouveau_doc.ui"), self)

        self.doc_type_window = SelectDocTypeDialog()

        # Table sizing
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(0, 225)  # Reference d'Article
        self.tableWidget.setColumnWidth(1, 885)  # Designation
        self.tableWidget.setColumnWidth(2, 115)  # P.U.H.T
        self.tableWidget.setColumnWidth(3, 115)  # P.T.T.C
        self.tableWidget.setColumnWidth(4, 115)  # Qte
        self.tableWidget.setColumnWidth(5, 115)  # Taxe
        self.tableWidget.setColumnWidth(6, 115)  # Total TTC

        # Transparent buttons
        self.annule.setProperty("transparent", "true")
        self.suprimer.setProperty("transparent", "true")
        self.fermer.setProperty("transparent", "true")

        # Document type & number
        self.selected_doc_type = self.doc_type_window.get_selected_doc_type()
        self.setWindowTitle(f"Nouveau document - {self.selected_doc_type}")
        self.n_piece_editline.setText(generate_document_number(self.selected_doc_type))
        self.n_piece_editline.setReadOnly(True)
        self.n_piece_editline.setStyleSheet("color: gray;")

        # Clients LineEdit with autocomplete
        self.setup_clients_lineedit()

    def setup_table(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)

    @with_db_session
    def setup_clients_lineedit(self, session=None):
        line_edit: QLineEdit = self.clients_lineedit
        self._clients_autocomplete = LineEditAutoComplete(line_edit, self)

        query = (
            select(Tiers.nom_tiers)
            .where(Tiers.type_tiers == "CLIENT")
            .order_by(Tiers.nom_tiers)
        )
        # scalars() => list[str]
        names = session.execute(query).scalars().all()
        clients = [n for n in names if n]
        clients = self._normalize_client_names(clients)
        self._clients_autocomplete.set_items(clients)

        
    @staticmethod
    def _normalize_client_names(client_names):
        unique_names = []
        seen = set()

        for raw_name in client_names:
            if raw_name is None:
                continue

            normalized_name = str(raw_name).strip()
            if not normalized_name:
                continue

            key = normalized_name.casefold()
            if key in seen:
                continue

            seen.add(key)
            unique_names.append(normalized_name)

        unique_names.sort(key=str.casefold)
        return unique_names

        

    def current_selected_client(self) -> str:
        return self.clients_lineedit.text().strip()


def main():
    app = QApplication(sys.argv)
    window = NouveauDocWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()