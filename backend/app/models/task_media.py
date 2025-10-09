import datetime
from enum import Enum

from datetime import datetime, date, UTC

from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

from sqlmodel import SQLModel, Field, Relationship



from app.utils.security import generate_uid

class MediaTypes(str, Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    MP3 = "audio/mp3"
    MP4 = "video/mp4"
    MD = "text/markdown"

class TaskMedia(Base):
    __tablename__ = "task_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.id"))
    date: Mapped[date] = mapped_column(Date, ForeignKey("task.date"))
    info: Mapped[str] = mapped_column(String,nullable=True)
    media_type: Mapped[MediaTypes] = mapped_column(String, default=MediaTypes.PNG)
    hint_number: Mapped[int] = mapped_column(Integer, default=0)

    uuid: Mapped[str] = mapped_column(String, unique=True, default_factory=lambda: generate_uid())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)



# def is_locked(self, user, session) -> bool:
#     match self.task.status:
#         case "closed": return True
#         case "expired": return False
#         case "open":
#             if task_tracker := TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session):
#                 return self.hint_number > task_tracker.hints_used
#         case _:
#             return False
#
#     if task_tracker := TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session):
#         return self.hint_number > task_tracker.hints_used
#
#     return False
