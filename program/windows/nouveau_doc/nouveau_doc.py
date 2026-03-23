import os
import sys

from PyQt5.QtWidgets import (QDialog,
                             QApplication, QMainWindow,
                             QTableWidgetItem,
                             QHeaderView,
                             QLineEdit,
                             QComboBox)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

from program.services import (generate_document_number,
                              with_db_session,
                              select,
                              insert,
                              Tiers,
                              Article,
                              and_,
                              Document,
                              replace_combobox_with_lineedit,
                              get_colored_icon,
                              LineEditAutoComplete)
from .select_doc_type import SelectDocTypeDialog


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class NouveauDocWindow(QMainWindow):
    def __init__(self):
        super(NouveauDocWindow, self).__init__()
        loadUi(resource_path("doc.ui"), self)

        self._setup_table()
        self._setup_defaults()
        self._setup_icons()
        

    def _setup_table(self):
        """Configure the document lines table."""
        header = self.tableWidget.horizontalHeader()
        # Stretch Designation column, fix the rest
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)   # Designation expands

        self.tableWidget.setColumnWidth(0, 150)   # Reference Article
        self.tableWidget.setColumnWidth(2, 100)   # P.U.H.T
        self.tableWidget.setColumnWidth(3, 100)   # P.T.T.C
        self.tableWidget.setColumnWidth(4, 70)    # Qte
        self.tableWidget.setColumnWidth(5, 80)    # Taxe
        self.tableWidget.setColumnWidth(6, 110)   # Totale TTC

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setRowCount(0)

        self.doc_type_window = SelectDocTypeDialog()
        self.selected_doc_type = self.doc_type_window.get_current_doc_type()
        self.setWindowTitle(f"Nouveau document - {self.selected_doc_type}")
        self.ndocument_lineedit.setText(generate_document_number(self.selected_doc_type))
        self.ndocument_lineedit.setReadOnly(True)

        # Clients LineEdit with autocomplete
        self._setup_clients_lineedit()
        self._setup_articles_combobox()

    def _setup_defaults(self):
        """Set sensible default values for form fields."""
        self.date_dateedit.setDate(QDate.currentDate())
        self.qte_lineedit.setText("1")
        self.ttc_lineedit.setReadOnly(True)
        self.total_tax_label.setReadOnly(True)
        self.total_UT_label.setReadOnly(True)
        self.total_ttc_label.setReadOnly(True)

        # Lock entry fields until document is validated
        self._set_entry_fields_enabled(False)

    def _set_entry_fields_enabled(self, enabled: bool) -> None:
        """Enable or disable all article entry fields and their action buttons."""
        for widget_name in (
            'articles_combobox',
            'designation_editline',
            'puht_editline',
            'pttc_editline',
            'qte_lineedit',
            'taxe_editline',
        ):
            w = getattr(self, widget_name, None)
            if w:
                w.setEnabled(enabled)

        for btn_name in ('annule', 'enrgistrer', 'suprimer'):
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setEnabled(enabled)


    def _setup_icons(self):
        """Apply colored icons to buttons."""
        # Set white print icon
        self.btn_imprimer.setIcon(get_colored_icon('../../assets/global/print.svg', '#ffffff'))
        self.btn_imprimer.setIconSize(QSize(16, 16))
        
        # Set white icon for nouveau button
        self.btn_nouveau.setIcon(get_colored_icon('../../assets/global/add.svg', '#ffffff'))
        self.btn_nouveau.setIconSize(QSize(80, 80))

    # ── Entry-row helpers ────────────────────────────────────────────────────

    
    
    @with_db_session
    def _setup_clients_lineedit(self, session=None):
        line_edit: QLineEdit = self.clients_lineedit
        # Store the original stylesheet from the UI file
        original_stylesheet = line_edit.styleSheet()
        # Create the autocomplete functionality
        self._clients_autocomplete = LineEditAutoComplete(line_edit, self)
        # Ensure the original stylesheet is preserved
        if original_stylesheet:
            line_edit.setStyleSheet(original_stylesheet)
        stmt = (
            select(Tiers.nom_tiers)
            .where(Tiers.type_tiers == "CLIENT")
            .order_by(Tiers.nom_tiers)
        )
        # scalars() => list[str]
        names = session.execute(stmt).scalars().all()
        clients = [n for n in names if n]
        clients = self._normalize_client_names(clients)
        self._clients_autocomplete.set_items(clients)
        self.clients_lineedit.textChanged.connect(lambda: _on_client_name_text_changed(self.clients_lineedit.text()))
        self.clientid_lineedit.textChanged.connect(lambda: _on_client_id_text_changed(self.clientid_lineedit.text()))



        def _on_client_name_text_changed(lineedit_text):
            if self.clients_lineedit.hasFocus():
                if lineedit_text.strip() == "":
                    self.clientid_lineedit.clear()
                else:
                    stmt = (select(Tiers.code_tiers)
                            .where(and_(Tiers.type_tiers == "CLIENT",
                                        Tiers.nom_tiers.like(f"%{lineedit_text.strip()}%")))
                            .order_by(Tiers.nom_tiers).limit(1))
                    
                    result = session.execute(stmt).scalar_one_or_none()
                    self.clientid_lineedit.setText(result if result else "")
        
        def _on_client_id_text_changed(id_input_text):
            if self.clientid_lineedit.hasFocus():
                if id_input_text.strip() == "":
                    self.clients_lineedit.clear()
                else:
                    stmt = (select(Tiers.nom_tiers)
                            .where(and_(Tiers.type_tiers == "CLIENT",
                                        Tiers.code_tiers.like(f"%{id_input_text.strip()}%")))
                            .order_by(Tiers.nom_tiers).limit(1))
                    
                    result = session.execute(stmt).scalar_one_or_none()
                    self.clients_lineedit.setText(result if result else "")

    @with_db_session
    def _setup_articles_combobox(self, session=None):
        line_edit: QLineEdit = self.designation_editline
        # Store the original stylesheet from the UI file
        original_stylesheet = line_edit.styleSheet()
        # Create the autocomplete functionality
        self._designation_autocomplete = LineEditAutoComplete(line_edit, self)
        # Ensure the original stylesheet is preserved
        if original_stylesheet:
            line_edit.setStyleSheet(original_stylesheet)
        stmt = (
            select(Article.description)
            .where(Article.description.isnot(None))
            .order_by(Article.id_article)
        )
        # scalars() => list[str]
        names = session.execute(stmt).scalars().all()
        designations = [n for n in names if n]
        designations = self._normalize_client_names(designations)
        self._designation_autocomplete.set_items(designations)

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

