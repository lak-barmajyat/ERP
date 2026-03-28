import os
import sys

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

from .funcs import transfer_window_setup


def resource_path(relative_path: str) -> str:
    """Resolve a resource path relative to this file."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class TransfertDocumentDialog(QDialog):
    def __init__(
        self,
        parent=None,
        source_doc_id=None,
        source_doc_number=None,
        source_docs=None,
        default_operation="transfer",
    ) -> None:
        super().__init__(parent)
        loadUi(resource_path("transfert_document_dialog.ui"), self)

        transfer_window_setup(
            self,
            source_doc_id=source_doc_id,
            source_doc_number=source_doc_number,
            source_docs=source_docs,
            default_operation=default_operation,
        )


def main() -> None:
    app = QApplication(sys.argv)
    dialog = TransfertDocumentDialog()
    dialog.exec_()
    sys.exit(0)


if __name__ == "__main__":
    main()
