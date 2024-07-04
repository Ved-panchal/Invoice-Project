from fastapi import APIRouter, Depends
from routes import login_manager
from.dependencies import role_required

test_router = APIRouter()

@test_router.get("/hello")
def hello(user=Depends(role_required(['admin', 'user']))):
    # print(f"username: {user.username}")
    print(f"user: {user}")
    print(f"username: {user['username']}")
    return "hello"