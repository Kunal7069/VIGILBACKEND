from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from src.database.models.video import Video

class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, video_data: dict) -> Video:
        video = Video(**video_data)
        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def get(self, video_id: int) -> Optional[Video]:
        result = await self.db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Video]:
        result = await self.db.execute(select(Video))
        return result.scalars().all()

    async def update(self, video_id: int, update_data: dict) -> Optional[Video]:
        video = await self.get(video_id)
        if not video:
            return None
        for key, value in update_data.items():
            setattr(video, key, value)
        await self.db.commit()
        await self.db.refresh(video)
        return video