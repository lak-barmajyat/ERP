from __future__ import annotations
from program.services import (Tiers,
                            select,
                            with_db_session,
                            generate_document_number,
                            insert,
                            Document,
                            Article,
                            DetailDocument,
                            and_,
                            RefTypeDocument)
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QStringListModel, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QPalette, QColor
from datetime import datetime
import os


def show_error_message(message_text=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)  # أيقونة الخطأ الحمراء
    msg.setWindowTitle("Erreur")
    msg.setText(message_text)
    msg.setInformativeText("Veuillez vérifier les informations et réessayer.")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def create_document(data: dict, *, session):
    stmt = insert(Document).values(
        id_domaine=data["id_domaine"],
        id_type_document=data["id_type_document"],
        numero_document=data["numero_document"],
        id_tiers=data.get("id_tiers"),
        date_document=data["date_document"],
        date_livraison=data.get("date_livraison"),
        mode_prix=data.get("mode_prix", "HT"),
        total_ht=data.get("total_ht", 0),
        total_tva=data.get("total_tva", 0),
        total_ttc=data.get("total_ttc", 0),
        solde=data.get("solde", 0),
        id_vendeur=data["id_vendeur"],
        id_statut=data["id_statut"],
        commentaire=data.get("commentaire"),
    )

    result = session.execute(stmt)

    inserted_id = result.inserted_primary_key[0]
    return inserted_id

@with_db_session
def _valider(self, session=None):
    stmt = (select(Tiers.id_tiers)
            .where((Tiers.nom_tiers == self.clients_lineedit.text().strip()) &
                    (Tiers.code_tiers == self.clientidinput.text().strip()) &
                    (Tiers.type_tiers == "CLIENT")))
    result = session.execute(stmt).scalar_one_or_none()
    if not result:
        stmt = (select(Tiers.nom_tiers, Tiers.code_tiers)
                .where(and_(Tiers.type_tiers == "CLIENT",
                            Tiers.code_tiers == self.clientidinput.text().strip()))
                .order_by(Tiers.nom_tiers).limit(1))
        
        result = session.execute(stmt).scalar_one_or_none()
        if result:
            self.clients_lineedit.setText(result[0])
            self.clientidinput.setText(result[1])
        else:
            self.clients_lineedit.clear()
            self.clientidinput.clear()
        return

    id_type_document = session.execute(
        select(RefTypeDocument.id_type_document)
        .where(RefTypeDocument.code_type == self.selected_doc_type)
    ).scalar_one_or_none()

    if not id_type_document:
        show_error_message(f"Type de document '{self.selected_doc_type}' introuvable.")
        return

    document = Document(
        id_domaine=1,
        id_type_document=id_type_document,
        numero_document=self.n_piece_editline.text().strip(),
        id_tiers=session.execute(select(Tiers.id_tiers).where(and_(Tiers.nom_tiers == self.clients_lineedit.text().strip(), Tiers.type_tiers == "CLIENT"))).scalar_one_or_none(),
        date_document=self.dateEdit.date().toPyDate(),
        date_livraison=datetime.now().date(),
        mode_prix="HT",
        total_ht=0,
        total_tva=0,
        total_ttc=0,
        solde=0,
        id_vendeur=os.getenv('USER_ID', 6),  # default to 6 if not set
        id_statut=1,
        commentaire=""
        )

    session.add(document)
    session.commit()

    self.clients_lineedit.setReadOnly(True)
    self.clientidinput.setReadOnly(True)
    self.dateEdit.setReadOnly(True)
    self.btn_valider.setEnabled(False)

    self.current_document_id = document.id_document

def nouveau_doc_setup(nouveau_doc_window):
    result = nouveau_doc_window.doc_type_window.exec_()
    if result != QDialog.Accepted:
        return
    nouveau_doc_window.show()

    nouveau_doc_window.selected_doc_type = nouveau_doc_window.doc_type_window.get_selected_doc_type()
    nouveau_doc_window.setWindowTitle(f"Nouveau document - {nouveau_doc_window.selected_doc_type}")
    nouveau_doc_window.n_piece_editline.setText(generate_document_number(nouveau_doc_window.selected_doc_type))
    nouveau_doc_window.n_piece_editline.setReadOnly(True)

    nouveau_doc_window.btn_valider.clicked.connect(lambda: _valider(nouveau_doc_window))


    # you have to link database documents to their tables after creating them, so we load the articles for the new document (which will be empty)

    # and unlink id type tiers and link type tiers only

    # id_type_tiers will be the id to define the clients or the founissers by (CL001 , FR001)