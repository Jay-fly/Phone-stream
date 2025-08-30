import os
import secrets
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from livekit import api

load_dotenv()

app = FastAPI(title="LiveKit Viewer Token API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("LIVEKIT_API_KEY", "")
API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
SERVER_URL = os.getenv("LIVEKIT_SERVER_URL", "wss://your-project.livekit.cloud")

if not API_KEY or not API_SECRET:
    raise ValueError("請在 .env 文件中設置 LIVEKIT_API_KEY 和 LIVEKIT_API_SECRET")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    return FileResponse("static/assets/apple-icon-180.png", media_type="image/png")


@app.get("/apple-touch-icon-precomposed.png")
def apple_touch_icon_pre():
    return FileResponse("static/assets/apple-icon-180.png", media_type="image/png")


@app.get("/test", response_class=HTMLResponse)
async def root(request: Request):
    """提供觀看者前端頁面"""
    try:
        return templates.TemplateResponse("test.html", {"request": request})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>前端頁面未找到</h1><p>請確保 static/index.html 存在</p>")


@app.get("/", response_class=HTMLResponse)
async def mobile_publisher(request: Request):
    """提供手機直播發布者頁面"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>手機直播頁面未找到</h1><p>請確保 static/index2.html 存在</p>")


@app.get("/api/token")
async def get_token(room: str = "Drone-RTC-01") -> Dict[str, str]:
    """生成 LiveKit viewer token"""
    try:
        identity = f"viewer-{secrets.token_hex(4)}"
        at = (
            api.AccessToken(API_KEY, API_SECRET)
            .with_identity(identity)
            .with_grants(api.VideoGrants(room=room, room_join=True, can_subscribe=True, can_publish=False))
        )
        return {"identity": identity, "token": at.to_jwt(), "server_url": SERVER_URL, "room": room}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成 token 失敗: {str(e)}")


@app.get("/api/publisher-token")
async def get_publisher_token(room: str = "Drone-RTC-01", identity: str = None) -> Dict[str, str]:
    """生成 LiveKit publisher token（用於手機直播）"""
    try:
        # 如果沒有提供身份，自動生成一個
        if not identity:
            identity = f"mobile-publisher-{secrets.token_hex(4)}"

        at = (
            api.AccessToken(API_KEY, API_SECRET)
            .with_identity(identity)
            .with_grants(api.VideoGrants(room=room, room_join=True, can_subscribe=True, can_publish=True, can_publish_data=True))
        )
        return {"identity": identity, "token": at.to_jwt(), "server_url": SERVER_URL, "room": room}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成發布者 token 失敗: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
