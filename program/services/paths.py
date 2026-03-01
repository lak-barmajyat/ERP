# app/paths.py
from pathlib import Path

# Root: C:/Users/mlaktaou/Desktop/ERP
BASE_DIR     = Path(__file__).resolve().parent.parent.parent

# مجلد app
APP_DIR = BASE_DIR / "program"

# مجلد core
#CORE_DIR = APP_DIR / "core"

# مجلد services
SERVICES_DIR = APP_DIR / "services"

# مجلد windows
WINDOWS_DIR = APP_DIR / "windows"

# مجلد assets العام
ASSETS_DIR   = BASE_DIR / "program" / "assets"
ASSETS_LOGIN = ASSETS_DIR / "login"
ASSETS_ICONS = ASSETS_DIR / "icons"
ASSETS_FONTS = ASSETS_DIR / "fonts"

SQL_DIR      = BASE_DIR / "program" / "services" / "sql"
SQL_SCHEMA   = SQL_DIR / "ERP_database.sql"
SQL_SEED     = SQL_DIR / "fill_database.sql"