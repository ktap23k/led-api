from fastapi import FastAPI
from app.api.endpoints import items

app = FastAPI()

app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI app!"}

# @app.get("/list-routers")
# def list_routers():
#     routes_info = []
#     for route in app.routes:
#         routes_info.append({
#             "path": route.path,
#             "name": route.name,
#             "methods": route.methods
#         })
#     return {"routes": routes_info}
