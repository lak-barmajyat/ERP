from program import *
import bcrypt
import re


@with_db_connection(dict_cursor=False)
def add_user(username, password, role="user", cursor=None) -> bool:
    query = "SELECT 1 FROM utilisateurs WHERE nom_utilisateur=%s LIMIT 1"
    cursor.execute(query, (username,))
    if cursor.fetchone(): return False

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    query = """
        INSERT INTO `utilisateurs`
        (`id_utilisateur`, `nom_utilisateur`, 
        `mot_de_passe_hash`, `role`, `permissions_json`, 
        `actif`, `created_at`, `updated_at`) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (username, hashed_password, role))
    return True


def validate_password(password: str, messages: dict | None = None) -> tuple[bool, str]:

    default_messages = {
        "length": "Password must be at least 8 characters long",
        "uppercase": "Password must contain at least one uppercase letter",
        "lowercase": "Password must contain at least one lowercase letter",
        "digit": "Password must contain at least one number",
        "special": "Password must contain at least one special character",
        "success": "Password is strong"
    }

    if messages:
        default_messages.update(messages)

    if len(password) < 8:
        return False, default_messages["length"]

    if not re.search(r"[A-Z]", password):
        return False, default_messages["uppercase"]

    if not re.search(r"[a-z]", password):
        return False, default_messages["lowercase"]

    if not re.search(r"[0-9]", password):
        return False, default_messages["digit"]

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, default_messages["special"]

    return True, default_messages["success"]
