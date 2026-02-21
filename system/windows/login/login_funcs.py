from program import get_db_connection, close_db_connection, USERNAME, USER_ROLE
from program.windows.dashboard.dashboard import DashboardWindow
import bcrypt
from program.services.db_helper_funcs import fetch_one


def authenticate_user(username, password, cursor):
    query = "SELECT mot_de_passe_hash FROM utilisateurs WHERE nom_utilisateur = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result is None:
        return False

    stored_hash = result[0]

    return bcrypt.checkpw(password.encode(), stored_hash.encode())


def check_user(login):
    global USERNAME, USER_ROLE

    connect, cursor = get_db_connection()

    username = login.utilisateur_lineedit.text().strip()
    password = login.mot_de_pass_lineedit.text()

    if not username or not password:
        login.connection_error_label.setText("Veuillez remplir tous les champs.")
        login.connection_error_label.show()
        close_db_connection(connect, cursor)
        return

    if not authenticate_user(username, password, cursor):
        login.connection_error_label.setText("Nom d'utilisateur ou mot de passe incorrect.")
        login.connection_error_label.show()
        close_db_connection(connect, cursor)
        return

    USERNAME = username
    result = fetch_one("SELECT `role` FROM utilisateurs WHERE nom_utilisateur = %s", (username,))
    if result:
        USER_ROLE = result[0]

    login.connection_error_label.hide()
    close_db_connection(connect, cursor)
    dashboard = DashboardWindow()
    login.dashboard = dashboard
    dashboard.show()
    login.close()
