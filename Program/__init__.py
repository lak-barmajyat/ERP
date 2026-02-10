from pathlib import Path

#================== Paths ==================#

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "program"
#CORE_DIR = APP_DIR / "core"
SERVICES_DIR = APP_DIR / "services"
WINDOWS_DIR = APP_DIR / "windows"
ASSETS_DIR = APP_DIR / "assets"

#============= Global Variables =============#

USERNAME = None
USER_ROLE = None
USER_PERMISSIONS = None

#===================== Imports ==================#

from program.services.db_connection import close_db_connection, get_db_connection
from program.windows.dashboard.dashboard import DashboardWindow
from program.windows.login.login import LoginWindow
from program.windows.login.login_funcs import check_user


__all__ = [
    "DashboardWindow",
    "LoginWindow",
    "check_user",
    "get_db_connection",
    "close_db_connection",
    "BASE_DIR",
    "APP_DIR",
    "SERVICES_DIR",
    "WINDOWS_DIR",
    "ASSETS_DIR",
    "USERNAME",
    "USER_ROLE",
    "USER_PERMISSIONS"
]
