from fastapi.security import OAuth2PasswordBearer
from fastapi_login import LoginManager
from pathlib import Path
from decouple import config
import os

SECRET = config('LOGIN_SECRET')

login_manager = LoginManager(SECRET, token_url='/auth/token', use_cookie=True)

login_manager_v2 = LoginManager(SECRET, token_url='/auth/token', use_cookie=False)

# Creae static folder if does not exist
user_dir = Path("static")
if not user_dir.exists():
    os.makedirs(user_dir)

# Static folder
STATIC_DIR = Path("static")
