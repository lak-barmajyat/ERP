from program.services import Tiers, select, with_db_session

@with_db_session
def nouveau_doc_setup(nouveau_doc_window, session):
    nouveau_doc_window.show()

    query = select(Tiers.nom_tiers).where(Tiers.type_tiers == 'client').order_by(Tiers.nom_tiers)
    clients = session.execute(query).fetchall()
    nouveau_doc_window.clients_combobox.addItems([client[0] for client in clients])