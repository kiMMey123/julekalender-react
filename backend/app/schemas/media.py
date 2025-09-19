import datetime

import pydantic
from pydantic import HttpUrl, field_serializer
from sqlalchemy import UniqueConstraint, Column, JSON
from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import Optional, List, Literal

from app.database import session_scope
from app.utils.encryption import enigma
from app.utils.security import generate_uid

from enum import Enum

class MediaTypes(str, Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    MP3 = "audio/mp3"
    MP4 = "video/mp4"
    MD = "text/markdown"

class TaskMedia(SQLModel, table=True):
    date: datetime.date = Field(default=datetime.date.today(), primary_key=True)
    media_type: MediaTypes
    description: dict = Field(default=None, sa_column=Column(JSON))
    file_name: Optional[str] = Field(default=None)