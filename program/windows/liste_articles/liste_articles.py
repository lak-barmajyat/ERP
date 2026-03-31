import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QHeaderView,
    QTableWidgetItem,
    QWidget,
)
from PyQt5.uic import loadUi

from program.themes.shared_input_popup_style import apply_input_styles_to_window

from .funcs import liste_articles_setup


LISTE_ARTICLES_STYLE_MAP = {
    "__window__": ["QWidget", "global_font"],
    "__all_lineedits__": ["QLineEdit", "entry"],
    "__all_comboboxes__": ["QComboBox", "combobox"],
    "__all_dateedits__": ["QDateEdit", "dateedit"],
    "__all_combobox_popups__": ["QComboBox", "popup_list", {"row_height": 36}],
    "__all_completer_popups__": ["QLineEdit", "completer_popup", {"row_height": 36}],
    "btnFilter": ["QPushButton", "primary"],
    "btnClearFilters": ["QPushButton", "primary"],
    "tbNew": ["QToolButton", "toolbar"],
    "tbEdit": ["QToolButton", "toolbar"],
    "tbDelete": ["QToolButton", "toolbar"],
    "tbExportExcel": ["QToolButton", "toolbar"],
}


def resource_path(relative_path: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ArticlesWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        loadUi(resource_path("liste_articles.ui"), self)

        self._apply_ui_overrides()
        self._setup_table()
        self._setup_defaults()
        liste_articles_setup(self)
        apply_input_styles_to_window(self, row_height=36, widget_styles_map=LISTE_ARTICLES_STYLE_MAP)

    def _apply_ui_overrides(self) -> None:
        self.setWindowTitle("Articles")

        for name in (
            "tbPrint",
            "tbDuplicate",
            "tbTransform",
            "tbReplace",
            "toolbarDivider2",
            "toolbarDivider2_2",
        ):
            w = getattr(self, name, None)
            if w is not None:
                w.hide()

        for name in (
            "labelDocNumber",
            "editDocNumber",
            "labelPeriod",
            "labelPeriodDash",
            "dateFrom",
            "dateTo",
        ):
            w = getattr(self, name, None)
            if w is not None:
                w.hide()

        if hasattr(self, "labelcodeclient"):
            self.labelcodeclient.setText("Référence")
        if hasattr(self, "editcodeclient"):
            self.editcodeclient.setPlaceholderText("ART0001")
        if hasattr(self, "labelClient"):
            self.labelClient.setText("Article")
        if hasattr(self, "editClient"):
            self.editClient.setPlaceholderText("Rechercher un article...")
        if hasattr(self, "labelDocType"):
            self.labelDocType.setText("Famille")

        if hasattr(self, "labelStatus"):
            self.labelStatus.setText("Stock")

        if hasattr(self, "labelNbDocumentsTitle"):
            self.labelNbDocumentsTitle.setText("Nb Articles")
        if hasattr(self, "labelTotalHtTitle"):
            self.labelTotalHtTitle.setText("Sous minimum")

        for name in (
            "labelTotalTtcTitle",
            "labelTotalTtcValue",
            "summaryTotalBalanceFrame",
        ):
            w = getattr(self, name, None)
            if w is not None:
                w.hide()

    def _setup_table(self) -> None:
        if not hasattr(self, "tableDocuments"):
            return

        self.tableDocuments.setColumnCount(9)  # 8 visible (incl. checkbox) + 1 hidden ID
        headers = [
            "",
            "Référence",
            "Nom article",
            "Famille",
            "Prix vente HT",
            "Prix achat HT",
            "TVA",
            "Qte",
            "ID",
        ]
        for idx, label in enumerate(headers):
            self.tableDocuments.setHorizontalHeaderItem(idx, QTableWidgetItem(label))
        self.tableDocuments.setColumnHidden(8, True)

        header = self.tableDocuments.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tableDocuments.setColumnWidth(0, 34)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        for idx in (4, 5, 6, 7):
            header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)

        self.tableDocuments.verticalHeader().setVisible(False)
        self.tableDocuments.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableDocuments.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableDocuments.setSortingEnabled(True)
        self.tableDocuments.setAlternatingRowColors(True)

    def _setup_defaults(self) -> None:
        if hasattr(self, "labelNbDocumentsValue"):
            self.labelNbDocumentsValue.setText("0")
        if hasattr(self, "labelTotalHtValue"):
            self.labelTotalHtValue.setText("0")


def main() -> None:
    app = QApplication(sys.argv)
    window = ArticlesWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
