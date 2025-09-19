import datetime

import pydantic
from pydantic import HttpUrl, field_serializer
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import Optional, List, Literal

from app.database import session_scope
from app.utils.encryption import enigma
from app.utils.security import generate_uid

from enum import Enum

def get_open_close_time(date, hour):
    date_time = datetime.datetime.combine(date, datetime.datetime.min.time())
    return date_time.replace(hour=hour, minute=0, second=0, microsecond=0)


class MediaTypes(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"


class Task(SQLModel, table=True):
    date: datetime.date = Field(default=datetime.date.today(), primary_key=True, unique=True)
    open_time: datetime.datetime = Field(nullable=False)
    close_time: datetime.datetime = Field(nullable=False)
    info: str = Field(nullable=False)
    media: MediaTypes = Field(nullable=False)
    media_url: Optional[str] = Field(nullable=True)
    yt_url: Optional[str] = Field(nullable=True)
    answer: "TaskAnswer" = Relationship(back_populates="task", cascade_delete=True)
    hints: List["TaskHint"] = Relationship(back_populates="task", cascade_delete=True)

    @classmethod
    def get_active_task(cls, session: Session) -> Optional["Task"]:
        today = datetime.date.today()
        task = session.exec(select(cls).where(cls.date == today)).first()
        return task

    def check_answer(self, text, session) -> bool:
        return enigma.compare_answer(text, self.answer.text)

    @property
    def is_active(self):
        now = datetime.datetime.now()
        return self.open_time < now < self.close_time

class TaskCreate(pydantic.BaseModel):
    info: str
    media: MediaTypes
    media_url: Optional[HttpUrl]
    yt_url: Optional[HttpUrl]
    author: Optional[str]
    answer: str
    open_time: int = pydantic.Field(default=9, ge=6, le=22)
    close_time: int = pydantic.Field(default=23, gt=19, le=23)

    def to_task_dict(self, date) -> dict:
        data = self.model_dump()
        if self.media_url is not None:
            data["media_url"] = self.media_url.unicode_string()
        else:
            data["media_url"] = ""

        if self.yt_url is not None:
            data["yt_url"] = self.yt_url.unicode_string()
        else:
            data["yt_url"] = ""
        data["open_time"]  = get_open_close_time(date, data["open_time"])
        data["close_time"] = get_open_close_time(date, data["close_time"])
        return data

class TaskHint(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, foreign_key="task.date")
    info: Optional[str] = Field(nullable=True)
    media: MediaTypes = Field(nullable=False)
    media_url: Optional[str] = Field(nullable=True)
    hint_number: int = Field(primary_key=True, nullable=False, le=5)
    task: Task = Relationship(back_populates="hints")

    __table_args__ = (
        UniqueConstraint("date", "hint_number"),
    )

class TaskHintCreate(pydantic.BaseModel):
    info: Optional[str]
    media: MediaTypes
    media_url: Optional[str]


class TaskAnswer(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, unique=True, foreign_key="task.date")
    text: str = Field(nullable=False)
    task: Task = Relationship(back_populates="answer")


