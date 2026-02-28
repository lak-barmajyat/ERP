from program.services.db_connection import *
import bcrypt
from PyQt5.QtWidgets import QApplication
from program.windows.dashboard import DashboardWindow, dashboard_setup
from program.services.db_connection import with_db_session
from program.services import Utilisateur, select


def authenticate_user(username, password, session):
    query = (
        select(Utilisateur.mot_de_passe_hash)
        .where(Utilisateur.nom_utilisateur == username)
        .limit(1)
    )
    result = session.execute(query).first()

    if result is None:
        return False

    stored_hash = result[0]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    return bcrypt.checkpw(password.encode(), stored_hash)


@with_db_session
def check_user(login, session):

    username = login.utilisateur_lineedit.text().strip()
    password = login.mot_de_pass_lineedit.text()

    if not username or not password:
        login.connection_error_label.setText("Veuillez remplir tous les champs.")
        login.connection_error_label.show()
        return

    if not authenticate_user(username, password, session):
        login.connection_error_label.setText("Nom d'utilisateur ou mot de passe incorrect.")
        login.connection_error_label.show()
        return

    login.connection_error_label.hide()
    login.close()

    app = QApplication.instance()          # get the running app
    app._dashboard_window = DashboardWindow()   # keep reference alive on app
    dashboard_setup(app._dashboard_window)
