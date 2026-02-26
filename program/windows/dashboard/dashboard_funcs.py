from .dashboard import DashboardWindow
from program.windows.nouveau_doc import NouveauDocWindow, nouveau_doc_setup


def dashboard_setup(dashboard_window):
    dashboard_window.show()

    dashboard_window.nouveau_doc_window = NouveauDocWindow()

    dashboard_window.nouveau_doc.clicked.connect(lambda: nouveau_doc_setup(dashboard_window.nouveau_doc_window))