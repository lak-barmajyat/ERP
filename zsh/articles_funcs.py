from program import with_db_connection


@with_db_connection(dict_cursor=False)
def add_article(data: dict, cursor=None) -> bool:
    check_query = "SELECT 1 FROM articles WHERE nom_article = %s LIMIT 1"
    cursor.execute(check_query, (data["nom_article"],))
    if cursor.fetchone(): return False

    query = """
        INSERT INTO articles (
            nom_article, description, prix_vente_ht, prix_achat_ht,
            id_famille, taux_tva, suivi_stock, unite, reference_interne,
            code_barres, actif, created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, NOW(), NOW()
        )
    """

    cursor.execute(query, (
        data["nom_article"], data.get("description", ""), data["prix_vente_ht"], data["prix_achat_ht"],
        data["id_famille"], data["taux_tva"], data.get("suivi_stock", 1), data.get("unite", "pcs"),
        data.get("reference_interne"), data.get("code_barres"), data.get("actif", 1),
    ))
    return True