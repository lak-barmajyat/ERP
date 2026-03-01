from __future__ import annotations
from program.services import (Tiers,
                            select,
                            with_db_session,
                            generate_document_number,
                            insert,
                            Document,
                            Article,
                            DetailDocument)
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QStringListModel, Qt, QSortFilterProxyModel
from datetime import datetime


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
def valider_doc(nouveau_doc_window, session=None):
    client_name = nouveau_doc_window.clients_lineedit.text().strip()
    stmt = select(Tiers).where(Tiers.nom_tiers == client_name, Tiers.type_tiers == "CLIENT")
    client = session.execute(stmt).scalar_one_or_none()
    if not client:
        show_error_message("Client non trouvé. Veuillez sélectionner un client valide.")
        return

    date = nouveau_doc_window.dateEdit.date().toPyDate()
    if date > datetime.now().date():
        show_error_message("La date ne peut pas être dans le futur.")
        return

    n_piece = nouveau_doc_window.n_piece_editline.text().strip()

    create_document({
        "id_domaine": 1,
        "id_type_document": nouveau_doc_window.selected_doc_type,
        "numero_document": n_piece,
        "id_tiers": client.id_tiers,
        "date_document": date,
        "date_livraison": None,
        "mode_prix": "HT",
        "total_ht": float(0),
        "total_tva": float(0),
        "total_ttc": float(0),
        "solde": float(0),
        "id_vendeur":4,
        "id_statut": 1,
        "commentaire": "",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }, session=session)

    nouveau_doc_window.clients_lineedit.setReadOnly(True)
    nouveau_doc_window.valider_button.setEnabled(False)


@with_db_session
def fetch_doc_articles(doc_id: int, *, session):
    stmt = (
        select(
            Article.reference_interne,          # Référence d'article
            Article.nom_article,                # Désignation
            DetailDocument.prix_unitaire_ht,    # P.U.H.T
            DetailDocument.total_ligne_ttc,     # P.T.T.C (المجموع TTC للسطر)
            DetailDocument.quantite             # Qte
        )
        .join(DetailDocument, DetailDocument.id_article == Article.id_article)
        .where(DetailDocument.id_document == doc_id)
        .order_by(DetailDocument.id_detail.asc())
    )

    rows = session.execute(stmt).all()
    # rows = list of tuples: (ref, name, pu_ht, pt_ttc, qte)
    return rows

def load_doc_articles_into_table(nouveau_doc_window, doc_id: int):
    rows = fetch_doc_articles(doc_id)

    nouveau_doc_window.tableWidget.setRowCount(len(rows))

    for r, (ref, name, pu_ht, pt_ttc, qte) in enumerate(rows):
        values = [
            ref or "",
            name or "",
            f"{float(pu_ht):.2f}" if pu_ht is not None else "0.00",
            f"{float(pt_ttc):.2f}" if pt_ttc is not None else "0.00",
            f"{float(qte):.3f}" if qte is not None else "0.000",
        ]

        for c, v in enumerate(values):
            item = QTableWidgetItem(v)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # read-only
            nouveau_doc_window.tableWidget.setItem(r, c, item)

    nouveau_doc_window.tableWidget.resizeColumnsToContents()


def nouveau_doc_setup(nouveau_doc_window):
    result = nouveau_doc_window.doc_type_window.exec_()
    if result != QDialog.Accepted:
        return
    nouveau_doc_window.show()

    nouveau_doc_window.selected_doc_type = nouveau_doc_window.doc_type_window.get_selected_doc_type()
    nouveau_doc_window.setWindowTitle(f"Nouveau document - {nouveau_doc_window.selected_doc_type}")
    nouveau_doc_window.n_piece_editline.setText(generate_document_number(nouveau_doc_window.selected_doc_type))
    nouveau_doc_window.n_piece_editline.setReadOnly(True)
    nouveau_doc_window.n_piece_editline.setStyleSheet("color: gray;")

    nouveau_doc_window.valider.clicked.connect(lambda: valider_doc(nouveau_doc_window))


    # you have to link database documents to their tables after creating them, so we load the articles for the new document (which will be empty)

    # and unlink id type tiers and link type tiers only

    # id_type_tiers will be the id to define the clients or the founissers by (CL001 , FR001)