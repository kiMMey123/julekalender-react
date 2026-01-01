import datetime
from datetime import datetime, date, UTC
from enum import Enum

from sqlalchemy import Date, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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
    info: Mapped[str] = mapped_column(String, nullable=True)

    file_name: Mapped[str] = mapped_column(String, unique=True)
    media_type: Mapped[MediaTypes] = mapped_column(String, nullable=False)

    hint_number: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
