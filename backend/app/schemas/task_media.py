from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.core import TimestampSchema, PersistentDeletion
from app.settings import settings

class MediaTypes(dict, Enum):
    PNG = {"extension": "png", "format": "image/png"}
    JPG = {"extension": "jpg", "format": "image/jpeg"}
    JPEG = {"extension": "jpeg", "format": "image/jpeg"}
    MP3 = {"extension": "mp3", "format": "audio/mpeg"}
    MP4 = {"extension": "mp4", "format": "video/mp4"}
    MD = {"extension": "md", "format": "text/markdown"}

class TaskMediaBase(BaseModel):
    info: str

class TaskMedia(TimestampSchema, PersistentDeletion, TaskMediaBase):
    id: int
    task_id: int
    media_type: str


class TaskMediaRead(TaskMediaBase):
    pass


class TaskMediaCreate(TaskMediaBase):
    date: date
    hint_number: int
    info: str


class TaskMediaCreateInternal(TaskMediaCreate):
    task_id: int
    file_name: str
    media_type: str



class TaskMediaUpdate(BaseModel):
    pass


class TaskMediaUpdateInternal(TaskMediaUpdate):
    updated_at: datetime


class TaskMediaDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
