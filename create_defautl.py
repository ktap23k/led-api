import os

# Cấu trúc thư mục và file
project_structure = {
    "app": {
        "__init__.py": "",
        "main.py": '''from fastapi import FastAPI
from app.api.endpoints import users, items

app = FastAPI()

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI app!"}
''',
        "api": {
            "__init__.py": "",
            "endpoints": {
                "__init__.py": "",
                "users.py": '''from fastapi import APIRouter
from app.schemas.user import User
from app.services.user_service import create_user

router = APIRouter()

@router.get("/")
def get_users():
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

@router.post("/")
def add_user(user: User):
    return create_user(user)
''',
                "items.py": '''from fastapi import APIRouter
from app.schemas.item import Item

router = APIRouter()

@router.get("/")
def get_items():
    return [{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]

@router.post("/")
def add_item(item: Item):
    return {"item": item}
''',
            }
        },
        "core": {
            "__init__.py": "",
            "config.py": '''class Settings:
    PROJECT_NAME: str = "FastAPI Modular App"
    VERSION: str = "1.0.0"

settings = Settings()
''',
        },
        "models": {
            "__init__.py": "",
            "user.py": "",
            "item.py": "",
        },
        "schemas": {
            "__init__.py": "",
            "user.py": '''from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
''',
            "item.py": '''from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    description: str
''',
        },
        "services": {
            "__init__.py": "",
            "user_service.py": '''from app.schemas.user import User

def create_user(user: User):
    return {"message": "User created successfully", "user": user}
''',
            "item_service.py": "",
        },
    },
    "requirements.txt": '''fastapi==0.100.0
uvicorn==0.22.0
pydantic==1.10.7
'''
}

# Hàm tạo thư mục và file
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # Nếu là thư mục
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)  # Đệ quy tạo các mục con
        else:  # Nếu là file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Tạo cấu trúc trong thư mục hiện tại
create_structure(os.getcwd(), project_structure)
print("Project structure created successfully!")
