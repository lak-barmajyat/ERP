from program.windows.nouveau_doc import NouveauDocWindow, nouveau_doc_setup
from program.services import select, with_db_session, Utilisateur
from program.windows.dashboard import LogoutDialog

from PyQt5.QtWidgets import QDialog


# def logout(dashboard_window):
#     from program.windows.login import LoginWindow
#     logout_dialog = LogoutDialog()
#     if logout_dialog.exec_() == QDialog.Accepted:
#     dashboard_window.close()
#     login_window = LoginWindow()
#     login_window.show()

@with_db_session
def dashboard_setup(dashboard_window, session=None):
    dashboard_window.show()

    dashboard_window.nouveau_doc_window = NouveauDocWindow()

    dashboard_window.dashboard_widget.btn_nouveau_doc.clicked.connect(lambda: nouveau_doc_setup(dashboard_window.nouveau_doc_window))

    # dashboard_window.btn_logout.clicked.connect(lambda: logout(dashboard_window))

    role = session.execute(select(Utilisateur.role).where(Utilisateur.nom_utilisateur == dashboard_window.current_username)).scalar_one()
    dashboard_window.footerUserLabel.setText(f"Utilisateur: {dashboard_window.current_username}")
    dashboard_window.footerRoleLabel.setText(f"Rôle: {role}")