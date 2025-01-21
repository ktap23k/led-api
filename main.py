from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import items
from app.services.item_service import read_led_config, write_led_config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import pytz

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

timezone = pytz.timezone("Asia/Bangkok")  # UTC+7


def scheduled_task():
    print(f"Task executed at {datetime.datetime.now()}")
    # check if time is 6h, 12h, 18h UTC+7
    if datetime.datetime.now(timezone).hour == 6:
        data = {"led": 1, "seed": 40000}
    if datetime.datetime.now(timezone).hour == 12:
        data = {"led": 1, "seed": 60000}
    if datetime.datetime.now(timezone).hour == 18:
        data = {"led": 0, "seed": 0}
    write_led_config(data)


scheduler = BackgroundScheduler()

# Thêm job vào scheduler (chạy lúc 6h, 12h, 18h mỗi ngày)
trigger = CronTrigger(
    hour="6,12,18", minute=0, timezone=timezone
)  # Giờ: 6h, 12h, 18h, phút: 0
scheduler.add_job(scheduled_task, trigger=trigger)

scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/led", response_class=HTMLResponse)
def read_root(request: Request):
    config = read_led_config()
    return templates.TemplateResponse(
        "index.html", {"request": request, "config": config}
    )


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
