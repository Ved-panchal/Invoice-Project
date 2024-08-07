from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response
from decouple import config
from datetime import timedelta
import json

from routes import login_manager
from database import mongo_conn

login_router = APIRouter()

# Adjust the duration as needed
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES')

class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid username or password")

@login_manager.user_loader()
def load_user(username: str):  # could also be an asynchronous function
    user = mongo_conn.get_users_collection().find_one({'username' : username})
    return user

@login_router.post('/auth/token')
def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    try:
        username = data.username
        password = data.password

        user = load_user(username)
        if not user:
            raise InvalidCredentialsException()
        elif password != user['password']:
            raise InvalidCredentialsException()


        access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = login_manager.create_access_token(
            data=dict(sub=username, roles=user['role']),
            expires=access_token_expires
        )
        login_manager.set_cookie(response, access_token)
        response.status_code = 200
        response.body = json.dumps({"userId" : user["userId"]}).encode()

        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@login_router.post('/auth/logout')
def logout(response: Response):
    try:
        # Remove the authentication cookie
        response.delete_cookie(login_manager.cookie_name)
        response.status_code = 200
        response.body = json.dumps({"message": "Successfully logged out"}).encode()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
