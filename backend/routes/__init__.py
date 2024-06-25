from fastapi_login import LoginManager
from pathlib import Path
import os

SECRET = 'watashi-no-sacred-key'
login_manager = LoginManager(SECRET, token_url='/auth/token', use_cookie=True)

# Creae static folder if does not exist
user_dir = Path("static")
if not user_dir.exists():
    os.makedirs(user_dir)

# Static folder
STATIC_DIR = Path("static")
