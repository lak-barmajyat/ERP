from program import with_db_connection


@with_db_connection(dict_cursor=True)
def filter_documents(column_name: str, filter_value: str, cursor=None) -> list:
    query = f"SELECT * FROM documents WHERE {column_name} LIKE %s ORDER BY created_at DESC"
    cursor.execute(query, (f"%{filter_value}%",))
    return cursor.fetchall()


@with_db_connection(dict_cursor=False)
def add_document(data: dict, cursor=None):

    query = """
        INSERT INTO documents (
            id_domaine, id_type_document, numero_document, id_tiers, date_document, 
            date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, 
            id_vendeur, id_statut, commentaire, created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, NOW(), NOW()
        )
    """

    cursor.execute(query, (
        data["id_domaine"], data["id_type_document"], data["numero_document"], data["id_tiers"],
        data["date_document"], data.get("date_livraison"), data["mode_prix"], data["total_ht"],
        data["total_tva"], data["total_ttc"], data["solde"], data["id_vendeur"],
        data["id_statut"], data.get("commentaire", "")
    ))


@with_db_connection(dict_cursor=True)
def get_all_documents(cursor=None):
    query = "SELECT * FROM documents ORDER BY created_at DESC"
    cursor.execute(query)
    return cursor.fetchall()


@with_db_connection(dict_cursor=True)
def get_document_by_id(id_document: int, cursor=None):
    query = "SELECT * FROM documents WHERE id_document = %s"
    cursor.execute(query, (id_document,))
    return cursor.fetchone()


@with_db_connection(dict_cursor=False)
def update_document(id_document: int, data: dict, cursor=None):
    query = """
        UPDATE documents
        SET id_domaine=%s, id_type_document=%s, numero_document=%s, id_tiers=%s,
            date_document=%s, date_livraison=%s, mode_prix=%s, total_ht=%s,
            total_tva=%s, total_ttc=%s, solde=%s, id_vendeur=%s,
            id_statut=%s, commentaire=%s, updated_at=NOW()
        WHERE id_document=%s
    """
    cursor.execute(query, (
        data["id_domaine"], data["id_type_document"], data["numero_document"], data["id_tiers"],
        data["date_document"], data.get("date_livraison"), data["mode_prix"], data["total_ht"],
        data["total_tva"], data["total_ttc"], data["solde"], data["id_vendeur"],
        data["id_statut"], data.get("commentaire", ""),
        id_document
    ))


@with_db_connection(dict_cursor=False)
def delete_document(id_document: int, cursor=None):
    query = "DELETE FROM documents WHERE id_document = %s"
    cursor.execute(query, (id_document,))



def calculate_ttc(price_ht: float, taux_tva: float) -> float:
    return price_ht * (1 + taux_tva / 100)
