from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from enum import Enum
from src.database.models.video import VerificationEnum, StatusEnum

class VideoBase(BaseModel):
    crime_type: str
    video: str
    date: date
    time: time
    latitude: float
    longitude: float

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    crime_type: Optional[str]
    verification: Optional[VerificationEnum]
    status: Optional[StatusEnum]

class VideoOut(VideoBase):
    id: int
    verification: VerificationEnum
    status: StatusEnum

    class Config:
        orm_mode = True
        from_attributes = True