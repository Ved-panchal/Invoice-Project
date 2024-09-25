from fastapi import HTTPException, Depends
from routes import login_manager
from typing import List

def role_required(required_roles: List[str]):
    def role_checker(current_user: dict = Depends(login_manager)):
        user_roles = current_user['role']
        if not any(role in required_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return role_checker