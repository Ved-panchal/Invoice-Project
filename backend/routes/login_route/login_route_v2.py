from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response
from decouple import config
from datetime import timedelta
import json

from routes import login_manager_v2
from database import mongo_conn


login_router = APIRouter()

# Adjust the duration as needed
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES')

class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid username or password")

@login_manager_v2.user_loader()
def load_user(username: str):  # could also be an asynchronous function
    user = mongo_conn.get_users_collection().find_one({'username' : username})
    return user

@login_router.post('/auth/token', tags=["v2"])
def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    try:
        username = data.username
        password = data.password

        user = load_user(username)
        if not user:
            raise InvalidCredentialsException()
        elif password != user['password']:
            raise InvalidCredentialsException()

        access_token = login_manager_v2.create_access_token(
            data=dict(sub=username),expires=timedelta(minutes=float(60))
        )
        response.status_code = 200
        response.body = json.dumps({"access_token" : access_token, "token_type": "Bearer"}).encode()

        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@login_manager_v2._get_token
def load_token_from_header(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization Header")

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization Scheme")
    return token