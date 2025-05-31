
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.config import get_db
from src.services.crime_service import VideoService
from src.schemas.video import VideoCreate, VideoUpdate, VideoOut
from fastapi.encoders import jsonable_encoder
import shutil
import os
from datetime import date, time
from typing import List
import urllib.parse

router = APIRouter()

# UPLOAD_DIR = "./uploaded_videos"
# BASE_URL = "http://localhost:8000"  # Change to your backend base URL or make it configurable

# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @router.post("/videos/", response_model=VideoOut)
# async def create_video(
#     crime_type: str = Form(...),
#     video: UploadFile = File(...),
#     date: date = Form(...),
#     time: time = Form(...),
#     latitude: float = Form(...),
#     longitude: float = Form(...),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Save uploaded video file to disk
#     file_path = os.path.join(UPLOAD_DIR, video.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(video.file, buffer)

#     # URL-encode the filename to safely include spaces and special chars in URL
#     encoded_filename = urllib.parse.quote(video.filename)

#     # Build full URL accessible via your FastAPI static route
#     video_url = f"{BASE_URL}/uploaded_videos/{encoded_filename}"

#     video_data = {
#         "crime_type": crime_type,
#         "video": video_url,  # Save full URL in DB
#         "date": date,
#         "time": time,
#         "latitude": latitude,
#         "longitude": longitude,
#     }

#     service = VideoService(db)
#     saved_video = await service.create(video_data)
#     return saved_video

UPLOAD_DIR = "./uploaded_videos"
BASE_URL = "http://localhost:8000"

os.makedirs(UPLOAD_DIR, exist_ok=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        print(f"Broadcasting to {len(self.active_connections)} clients.")
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print("Broadcast error:", e)

manager = ConnectionManager()

@router.websocket("/ws/videos")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keeps the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# POST endpoint to upload a video
@router.post("/videos/", response_model=VideoOut)
async def create_video(
    crime_type: str = Form(...),
    video: UploadFile = File(...),
    date: date = Form(...),
    time: time = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: AsyncSession = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, video.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    encoded_filename = urllib.parse.quote(video.filename)
    video_url = f"{BASE_URL}/uploaded_videos/{encoded_filename}"

    video_data = {
        "crime_type": crime_type,
        "video": video_url,
        "date": date,
        "time": time,
        "latitude": latitude,
        "longitude": longitude,
    }

    service = VideoService(db)
    saved_video = await service.create(video_data)

    # ✅ Broadcast using model_dump() for Pydantic v2
    await manager.broadcast(jsonable_encoder(VideoOut.model_validate(saved_video)))

    return saved_video

@router.get("/videos/{video_id}", response_model=VideoOut)
async def read_video(video_id: int, db: AsyncSession = Depends(get_db)):
    service = VideoService(db)
    video = await service.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.get("/videos/", response_model=List[VideoOut])
async def read_all_videos(db: AsyncSession = Depends(get_db)):
    service = VideoService(db)
    videos = await service.get_all()
    return videos

@router.patch("/videos/{video_id}", response_model=VideoOut)
async def update_video(video_id: int, video_update: VideoUpdate, db: AsyncSession = Depends(get_db)):
    service = VideoService(db)
    video = await service.update(video_id, video_update.dict(exclude_unset=True))
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video
