from program.windows.nouveau_doc import NouveauDocWindow, nouveau_doc_setup


def logout(dashboard_window):
    from program.windows.login import LoginWindow
    dashboard_window.close()
    login_window = LoginWindow()
    login_window.show()

def dashboard_setup(dashboard_window):
    dashboard_window.show()

    dashboard_window.nouveau_doc_window = NouveauDocWindow()

    dashboard_window.dashboard_widget.btn_nouveau_doc.clicked.connect(lambda: nouveau_doc_setup(dashboard_window.nouveau_doc_window))

    dashboard_window.btn_logout.clicked.connect(lambda: logout(dashboard_window))