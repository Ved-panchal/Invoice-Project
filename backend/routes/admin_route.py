from fastapi import APIRouter, Depends
from starlette.responses import Response
from routes import login_manager
import json

from database import mongo_conn
from .dependencies import role_required

admin_router = APIRouter()
admin_router.prefix = '/admin'

@admin_router.get("/get_users")
def get_users(response: Response, current_user: dict = Depends(role_required(["admin"],login_manager))):
    users = []
    for user in mongo_conn.get_users_collection().find({}, {"_id": 0}):
        users.append(user)
    response.body = json.dumps({'users': users}).encode()
    response.status_code = 200
    return response