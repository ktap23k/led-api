from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import items
from app.services.item_service import read_led_config

app = FastAPI()

app.include_router(items.router, prefix="/items", tags=["items"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://led.mycode.vn", 
        "https://led.mycode.vn",
    ],  # Thay "*" bằng một danh sách cụ thể các origin được phép
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/statics"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/led", response_class=HTMLResponse)
def read_root(request: Request):
    config = read_led_config()
    return templates.TemplateResponse("index.html", {"request": request, "config": config})

@app.get("/logout", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})

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
