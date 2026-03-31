import os
import sys

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QAbstractItemView, QHeaderView, QTableWidgetItem, QWidget
from PyQt5.uic import loadUi

from program.themes.shared_input_popup_style import apply_input_styles_to_window

from .funcs import liste_clients_setup


LISTE_CLIENTS_STYLE_MAP = {
    "__window__": ["QWidget", "global_font"],
    "__all_lineedits__": ["QLineEdit", "entry"],
    "__all_comboboxes__": ["QComboBox", "combobox"],
    "__all_dateedits__": ["QDateEdit", "dateedit"],
    "__all_combobox_popups__": ["QComboBox", "popup_list", {"row_height": 36}],
    "__all_completer_popups__": ["QLineEdit", "completer_popup", {"row_height": 36}],
    "btnFilter": ["QPushButton", "primary"],
    "tbNew": ["QToolButton", "toolbar"],
    "tbEdit": ["QToolButton", "toolbar"],
    "tbDelete": ["QToolButton", "toolbar"],
    "tbDuplicate": ["QToolButton", "toolbar"],
    "tbExportExcel": ["QToolButton", "toolbar"],
    "tbPrint": ["QToolButton", "toolbar"],
    "tbTransform": ["QToolButton", "toolbar"],
    "tbFermer": ["QToolButton", "toolbar"],
}


def resource_path(relative_path: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ClientsWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        loadUi(resource_path("liste_clients.ui"), self)

        self._apply_ui_overrides()
        self._setup_table()
        self._setup_defaults()
        liste_clients_setup(self)
        apply_input_styles_to_window(self, row_height=36, widget_styles_map=LISTE_CLIENTS_STYLE_MAP)

    def _apply_ui_overrides(self) -> None:
        self.setWindowTitle("Clients")

        # Optional toolbar buttons not implemented yet
        for name in ("tbPrint", "tbTransform", "tbFermer"):
            w = getattr(self, name, None)
            if w is not None:
                w.hide()

    def _setup_table(self) -> None:
        table = getattr(self, "tableClients", None)
        if table is None:
            return

        table.setColumnCount(11)  # 10 visible + 1 hidden ID
        headers = [
            "",
            "Code",
            "Nom / Raison Sociale",
            "ICE",
            "Téléphone",
            "Email",
            "Ville",
            "Plafond Crédit",
            "Solde",
            "Statut",
            "ID",
        ]
        for idx, label in enumerate(headers):
            table.setHorizontalHeaderItem(idx, QTableWidgetItem(label))
        table.setColumnHidden(10, True)

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        table.setColumnWidth(0, 34)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        for idx in (3, 4, 5, 6, 7, 8, 9):
            header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)

        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)

    def _setup_defaults(self) -> None:
        today = QDate.currentDate()
        if hasattr(self, "dateStart") and self.dateStart is not None:
            self.dateStart.setDate(today.addYears(-50))
        if hasattr(self, "dateEnd") and self.dateEnd is not None:
            self.dateEnd.setDate(today)

        if hasattr(self, "lblSelection"):
            self.lblSelection.setText("0 client sélectionné")
        if hasattr(self, "lblTotalClients"):
            self.lblTotalClients.setText("0")
        if hasattr(self, "lblTotalSolde"):
            self.lblTotalSolde.setText("0,00 MAD")


def main() -> None:
    app = QApplication(sys.argv)
    window = ClientsWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
