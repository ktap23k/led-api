from app.schemas.user import User

def create_user(user: User):
    return {"message": "User created successfully", "user": user}
