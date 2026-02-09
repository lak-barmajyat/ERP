# app/paths.py
from pathlib import Path

# جذر المشروع ERP
BASE_DIR = Path(__file__).resolve().parent

# مجلد app
APP_DIR = BASE_DIR / "program"

# مجلد core
#CORE_DIR = APP_DIR / "core"

# مجلد services
SERVICES_DIR = APP_DIR / "services"

# مجلد windows
WINDOWS_DIR = APP_DIR / "windows"

# مجلد assets العام
ASSETS_DIR = APP_DIR / "assets"

# مجلد resources لكل نافذة
ASSETS_LOGIN = ASSETS_DIR / "login"