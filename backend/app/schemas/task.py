import datetime
from enum import Enum

import pydantic
from fastapi import HTTPException
from pydantic import HttpUrl
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import Optional, List, TYPE_CHECKING, Union

from starlette import status

from app.database import session_scope
from app.utils.encryption import enigma
from app.utils.security import generate_uid

if TYPE_CHECKING:
    from app.schemas.user import TaskTracker


def get_open_close_time(date, hour):
    date_time = datetime.datetime.combine(date, datetime.datetime.min.time())
    return date_time.replace(hour=hour, minute=0, second=0, microsecond=0)


class Task(SQLModel, table=True):
    date: datetime.date = Field(default=datetime.date.today(), primary_key=True, unique=True)
    open_time: datetime.datetime = Field(nullable=False)
    close_time: datetime.datetime = Field(nullable=False)
    info: str = Field(nullable=False)
    answer: "TaskAnswer" = Relationship(back_populates="task", cascade_delete=True)
    hints: List["TaskHint"] = Relationship(back_populates="task", cascade_delete=True)
    media: List["TaskMedia"] = Relationship(back_populates="task", cascade_delete=True)

    @classmethod
    def get_task(cls, session: Session, date: datetime.date = datetime.date.today()) -> Optional["Task"]:
        task = session.exec(select(cls).where(cls.date == date)).first()
        return task

    def to_admin_dict(self) -> "TaskAdminRead":
        admin_task_dict = self.model_dump()
        admin_task_dict["status"] = self.status

        if self.answer:
            admin_task_dict["answer_plaintext"] = enigma.decrypt_answer(self.answer.text)
            admin_task_dict["answer"] = self.answer.model_dump()

        admin_task_dict["media"] = self.media
        admin_task_dict["hints"] = self.hints

        return TaskAdminRead(**admin_task_dict)

    def check_answer(self, text) -> bool:
        return enigma.compare_answer(text, self.answer.text)

    @property
    def status(self) -> str:
        now = datetime.datetime.now()
        if self.open_time > now:
            return "closed"
        elif self.open_time < now < self.close_time:
            return "open"
        else:
            return "expired"


class TaskCreate(pydantic.BaseModel):
    info: str
    author: Optional[str]
    answer: str
    open_time: int = pydantic.Field(default=9, ge=6, le=22)
    close_time: int = pydantic.Field(default=23, gt=19, le=23)
    yt_url: Optional[HttpUrl]


class TaskUpdate(pydantic.BaseModel):
    info: Optional[str]
    author: Optional[str]
    answer: Optional[str]
    open_time: Optional[int] = pydantic.Field(default=9, ge=6, le=22)
    close_time: Optional[int] = pydantic.Field(default=23, gt=19, le=23)
    yt_url: Optional[HttpUrl]

class TaskUserRead(pydantic.BaseModel):
    date: datetime.date
    open_time: datetime.datetime
    close_time: datetime.datetime
    info: str
    status: str


class TaskAdminRead(TaskUserRead):
    answer_plaintext: str
    answer: dict
    hints: Optional[List["TaskHint"]]
    media: List["TaskMedia"]


class TaskHint(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, foreign_key="task.date")
    info: Optional[str] = Field(nullable=True)
    hint_number: int = Field(primary_key=True, nullable=False, le=5)
    task: Task = Relationship(back_populates="hints")

    __table_args__ = (
        UniqueConstraint("date", "hint_number"),
    )

class TaskHintCreate(pydantic.BaseModel):
    info: Optional[str]


class TaskAnswer(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, unique=True, foreign_key="task.date")
    text: str = Field(nullable=False)
    task: Task = Relationship(back_populates="answer")
    yt_url: Optional[str]

def create_or_update_task(data: Union[TaskCreate, TaskUpdate], date):
    try:
        with session_scope() as session:
            task_dict = {k: v for k, v in data.model_dump().items() if v is not None}

            for k, v in task_dict.items():
                match k:
                    case "open_time" | "close_time":
                        task_dict[k] = get_open_close_time(date, v)
                    case "answer":
                        task_dict[k] = enigma.encrypt_answer(task_dict.get("answer"))
                    case "yt_url":
                        task_dict[k] = task_dict.get("yt_url").unicode_string()

            answer_dict = {
                "text": task_dict.pop("answer", None),
                "yt_url": task_dict.pop("yt_url", None)
            }

            if task := Task.get_task(session, date):
                if task.status is not "closed":
                    raise HTTPException(status_code=403, detail="cannot edit open or expired task")
                for k, v in task_dict.items():
                    setattr(task, k, v)
                answer = task.answer
                for k, v in answer_dict.items():
                    if v is not None:
                        setattr(answer, k, v)


            else:
                task = Task(date=date, **task_dict)
                answer = TaskAnswer(date=date, **answer_dict)

            session.add(task)
            session.add(answer)
            session.commit()
            session.refresh(answer)
            session.refresh(task)
            return task.to_admin_dict()

    except IntegrityError as e:
        raise HTTPException(status_code=422, detail=str(e))

class MediaTypes(str, Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    MP3 = "audio/mp3"
    MP4 = "video/mp4"
    MD = "text/markdown"


class TaskMedia(SQLModel, table=True):
    file_name: str = Field(nullable=False, primary_key=True)
    hint_number: int = Field(default=0, nullable=False)
    date: datetime.date = Field(foreign_key="task.date")
    media_type: MediaTypes
    description: str = Field(nullable=True)
    task: "Task" = Relationship(back_populates="media")

    def is_locked(self, user, session) -> bool:
        match self.task.status:
            case "closed": return True
            case "expired": return False
            case "open":
                if task_tracker := TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session):
                    return self.hint_number > task_tracker.hints_used
            case _:
                return False

        if task_tracker := TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session):
            return self.hint_number > task_tracker.hints_used

        return False

    @classmethod
    def create_media_dict(cls, file, date, hint_number):
        file_name = generate_uid() + "." + file.filename.split(".")[-1]
        file_extension = file.filename.split(".")[-1]
        task_media_dict = {
            "date": date,
            "file_name": file_name,
            "media_type": MediaTypes[file_extension.upper()],
            "description": "desc",
            "hint_number": hint_number,
        }
        return cls(**task_media_dict)
