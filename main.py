import os
import secrets
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from livekit import api
from livekit.api import LiveKitAPI

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

# LiveKit API 客戶端會在需要時在異步函數中初始化

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
        # 檢查房間是否存在以及是否已有人在推流
        try:
            # 將 wss:// 或 ws:// 轉換為 https:// 或 http://
            http_server_url = SERVER_URL.replace("wss://", "https://").replace("ws://", "http://")
            
            # 在異步上下文中創建 LiveKit API 客戶端
            async with LiveKitAPI(
                url=http_server_url,
                api_key=API_KEY,
                api_secret=API_SECRET
            ) as livekit_client:
                rooms_response = await livekit_client.room.list_rooms(api.ListRoomsRequest())
                room_found = False
                for existing_room in rooms_response.rooms:
                    if existing_room.name == room:
                        room_found = True
                        if existing_room.num_publishers > 0:
                            raise HTTPException(status_code=409, detail=f"房間 {room} 目前已有人在推流，請稍後再試或選擇其他裝置")
                        break
                
                # 如果沒有找到房間，返回 404 錯誤
                if not room_found:
                    raise HTTPException(status_code=404, detail=f"房間 {room} 不存在，請檢查裝置名稱是否正確")
        except HTTPException:
            # 重新拋出 HTTP 異常
            raise
        except Exception as room_check_error:
            # 如果查詢房間狀態失敗，記錄錯誤但不阻止 token 生成
            print(f"警告：無法檢查房間狀態: {room_check_error}")

        # 如果沒有提供身份，自動生成一個
        if not identity:
            identity = f"mobile-publisher-{secrets.token_hex(4)}"

        at = (
            api.AccessToken(API_KEY, API_SECRET)
            .with_identity(identity)
            .with_grants(api.VideoGrants(room=room, room_join=True, can_subscribe=True, can_publish=True, can_publish_data=True))
        )
        return {"identity": identity, "token": at.to_jwt(), "server_url": SERVER_URL, "room": room}
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成發布者 token 失敗: {str(e)}")


@app.get("/api/devices")
async def get_devices() -> List[str]:
    """取得所有可用的裝置列表"""
    try:
        devices_env = os.getenv("DEVICES", "Drone-RTC-01")
        devices = [device.strip() for device in devices_env.split(",")]
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得裝置列表失敗: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
