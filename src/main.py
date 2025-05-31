from fastapi import FastAPI
from src.database.config import init_models
from src.api import crime_routes

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configure allowed origins
origins = [
    "http://localhost:3000",  # your React app URL
    # you can add more origins here, e.g., your production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins but not recommended for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
app.include_router(crime_routes.router)

@app.on_event("startup")
async def on_startup():
    await init_models()