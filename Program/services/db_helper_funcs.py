from program.services.db_connection import get_db_connection, close_db_connection
from functools import wraps


def with_db_connection(dict_cursor=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=dict_cursor)
            try:
                result = func(*args, cursor=cursor, conn=conn, **kwargs)
                conn.commit()
                return result
            except Exception:
                conn.rollback()
                raise
            finally:
                close_db_connection(conn, cursor)
        return wrapper
    return decorator


@with_db_connection
def fetch_one(query, params=None, cursor=None, conn=None):
    cursor.execute(query, params or ())
    result = cursor.fetchone()
    return result


@with_db_connection
def fetch_all(query, params=None, cursor=None, conn=None):
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    return result

@with_db_connection
def execute(query, params=None, commit=True, cursor=None, conn=None):
    cursor.execute(query, params or ())
    if commit:
        conn.commit()
    close_db_connection(conn, cursor)


def get_user_by_username(username):
    return fetch_one(
        "SELECT * FROM utilisateurs WHERE nom_utilisateur=%s",
        (username,)
    )


def build_where(filters: dict):
    clauses = []
    values = []

    for key, value in filters.items():
        clauses.append(f"{key}=%s")
        values.append(value)

    return " AND ".join(clauses), tuple(values)


def select(
    table: str,
    columns="*",
    where: dict | None = None,
    limit: int | None = None
):
    query = f"SELECT {columns} FROM {table}"
    params = ()

    if where:
        clause, params = build_where(where)
        query += f" WHERE {clause}"

    if limit:
        query += f" LIMIT {limit}"

    return fetch_all(query, params)


def insert(table: str, data: dict):
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))

    query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    execute(query, tuple(data.values()))


def exists(table: str, where: dict):
    where_clause, params = build_where(where)
    query = f"SELECT 1 FROM {table} WHERE {where_clause} LIMIT 1"
    return fetch_one(query, params) is not None
