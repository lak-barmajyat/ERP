from program import with_db_connection


@with_db_connection(dict_cursor=False)
def add_famille(data: dict, cursor=None) -> bool:
    check_query = "SELECT 1 FROM familles WHERE nom_famille = %s LIMIT 1"
    cursor.execute(check_query, (data["nom_famille"],))
    if cursor.fetchone(): return False
    

    query = """
        INSERT INTO familles (
            nom_famille, description, taux_tva, suivi_stock, unite_defaut, created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, %s, NOW(), NOW()
        )
    """
    cursor.execute(query, (
        data["nom_famille"],
        data.get("description", ""),
        data.get("taux_tva", 0),
        data.get("suivi_stock", 1),
        data.get("unite_defaut", "pcs")
    ))

    return True


@with_db_connection(dict_cursor=True)
def get_all_familles(cursor=None):
    query = "SELECT * FROM familles ORDER BY nom_famille ASC"
    cursor.execute(query)
    return cursor.fetchall()


@with_db_connection(dict_cursor=False)
def update_famille(id_famille: int, data: dict, cursor=None):
    query = """
        UPDATE familles
        SET nom_famille=%s,
            description=%s,
            taux_tva=%s,
            suivi_stock=%s,
            unite_defaut=%s,
            updated_at=NOW()
        WHERE id_famille=%s
    """
    cursor.execute(query, (
        data["nom_famille"],
        data.get("description", ""),
        data.get("taux_tva", 0),
        data.get("suivi_stock", 1),
        data.get("unite_defaut", "pcs"),
        id_famille
    ))


@with_db_connection(dict_cursor=False)
def delete_famille(id_famille: int, cursor=None):
    query = "DELETE FROM familles WHERE id_famille = %s"
    cursor.execute(query, (id_famille,))


@with_db_connection(dict_cursor=False)
def famille_exists(nom_famille: str, cursor=None):
    query = "SELECT 1 FROM familles WHERE nom_famille = %s LIMIT 1"
    cursor.execute(query, (nom_famille,))
    return cursor.fetchone() is not None

