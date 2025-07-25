import os
from fastapi import Depends, FastAPI, HTTPException, Query, status, Header, Request
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

import cv2
import uvicorn
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

last_frame = None

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
    if datetime.datetime.now(timezone).hour >= 18:
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


def verify_api_key(x_api_key: str = Header(None)):
    # Get the API key from environment variables
    APIKEY = os.getenv("API_KEYS")

    if x_api_key != APIKEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )


async def frame_generator():
    """Hàm tạo video stream từ các khung hình nhận được."""
    global last_frame
    while True:
        if last_frame is not None:
            # Mã hóa khung hình thành JPEG để hiển thị trên web
            (flag, encodedImage) = cv2.imencode(".jpg", last_frame)
            if not flag:
                continue

            # Yield the frame in the format required for multipart content
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
            )

        # Thêm một khoảng nghỉ nhỏ để giảm tải CPU
        await asyncio.sleep(0.01)


async def get_api_key(api_key_query: str = Query(None, alias="api_key")):
    # Ưu tiên key từ header, nếu không có thì lấy từ query
    API_KEY = os.getenv("API_KEYS")

    if api_key_query == API_KEY:
        return api_key_query

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


@app.get("/video_feed")
async def video_feed(api_key: str = Depends(get_api_key)):
    """Endpoint để xem video stream."""
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/video", response_class=HTMLResponse)
async def read_root(request: Request):
    """Phục vụ trang web chính bằng template stream_video.html."""
    return templates.TemplateResponse("stream_video.html", {"request": request})


@app.post("/upload")
async def upload_image(
    request: Request, api_key: str = Depends(verify_api_key)
):  # Sửa tham số thành request: Request
    """Endpoint để nhận ảnh trực tiếp từ request body."""
    global last_frame
    try:
        # Nhận toàn bộ dữ liệu binary từ request body
        contents = await request.body()

        npimg = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is not None:
            last_frame = frame
            return {"message": "Frame received successfully"}
        else:
            return {"message": "Failed to decode frame"}, 400

    except Exception as e:
        print(f"Error: {e}")
        return {"message": "Error processing frame"}, 500


from typing import List
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Quản lý các kết nối WebSocket của viewer."""

    def __init__(self):
        self.active_viewers: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_viewers.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_viewers.remove(websocket)

    async def broadcast_image(self, image_data: bytes):
        """Gửi dữ liệu hình ảnh đến tất cả các viewer."""
        if self.active_viewers:
            tasks = [viewer.send_bytes(image_data) for viewer in self.active_viewers]
            await asyncio.gather(*tasks, return_exceptions=False)

    async def broadcast_viewer_count(self):
        """Gửi số lượng viewer hiện tại đến tất cả viewer."""
        count_message = {"type": "viewers", "count": len(self.active_viewers)}
        if self.active_viewers:
            # Dùng websockets.broadcast tiện hơn gather
            # nhưng vì FastAPI không có sẵn nên dùng gather
            tasks = [viewer.send_json(count_message) for viewer in self.active_viewers]
            await asyncio.gather(*tasks, return_exceptions=False)


manager = ConnectionManager()


@app.get("/stream-cam")
async def get(request: Request):
    """Endpoint trả về trang web HTML."""
    return templates.TemplateResponse("stream_cam.html", {"request": request})


@app.websocket("/ws/viewer")
async def websocket_viewer_endpoint(
    websocket: WebSocket, api_key: str = Depends(get_api_key)
):
    """Endpoint cho các viewer (trình duyệt) kết nối."""
    await manager.connect(websocket)
    await manager.broadcast_viewer_count()  # Cập nhật số lượng cho mọi người
    try:
        while True:
            # Giữ kết nối mở, không cần nhận dữ liệu từ viewer
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_viewer_count()  # Cập nhật lại số lượng
        print("A viewer disconnected.")


@app.websocket("/ws/camera")
async def websocket_camera_endpoint(websocket: WebSocket):
    """Endpoint cho ESP32-CAM kết nối và gửi frame."""
    await websocket.accept()
    print("Camera connected.")
    try:
        while True:
            # Nhận dữ liệu hình ảnh dạng bytes từ camera
            image_bytes = await websocket.receive_bytes()
            # Broadcast hình ảnh đến tất cả các viewer đang kết nối
            await manager.broadcast_image(image_bytes)
    except WebSocketDisconnect:
        print("Camera disconnected.")
