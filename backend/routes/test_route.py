from fastapi import APIRouter, Depends
from routes import login_manager

test_router = APIRouter()

@test_router.get("/hello")
def hello(user=Depends(login_manager)):
    # print(f"username: {user.username}")
    print(f"user: {user}")
    print(f"username: {user['username']}")
    return "hello"

@test_router.get('/file')
def fileTest():
    return "hello from file"