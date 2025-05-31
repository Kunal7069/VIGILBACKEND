from sqlalchemy import Column, Integer, String, Float, Date, Time, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# Enums for verification and status
class VerificationEnum(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    unverified = "unverified"

class StatusEnum(str, enum.Enum):
    open = "open"
    closed = "closed"

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    crime_type = Column(String, nullable=False)
    video = Column(String, nullable=False)  # Can be URL or file path
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    verification = Column(Enum(VerificationEnum), default=VerificationEnum.pending, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.open, nullable=False)

