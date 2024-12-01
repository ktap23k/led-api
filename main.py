from fastapi import FastAPI
from app.api.endpoints import users, items
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI app!"}
