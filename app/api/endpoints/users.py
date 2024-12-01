from fastapi import APIRouter
from app.schemas.user import User
from app.services.user_service import create_user

router = APIRouter()

@router.get("/")
def get_users():
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
