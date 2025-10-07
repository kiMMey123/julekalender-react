import datetime

import pydantic
from pydantic import BaseModel, Field, HttpUrl, field_serializer, ConfigDict
from typing import Optional, List, TYPE_CHECKING, Annotated

from app.schemas.core import TimestampSchema
from app.utils.encryption import enigma
from app.utils.time import get_open_close_time



class TaskStatus(BaseModel):
    status: str | None = Field(default="closed")

    @field_serializer("status")
    def serialize_status(self, status: str) -> str:
        now = datetime.datetime.now()
        open_time = get_open_close_time(self.date, self.open_at)
        close_time = get_open_close_time(self.date, self.close_at)
        if open_time > now:
            return "closed"
        elif open_time < now < close_time:
            return "open"
        else:
            return "expired"


class TaskMediaRead(BaseModel):
    file_name: str
    description: str
    media_type: str


class TaskHintRead(BaseModel):
    info: str
    media: Optional[List[TaskMediaRead]]


class TaskBase(BaseModel):
    date: datetime.date
    info: str
    author: str = Field(min_length=2, max_length=30)
    open_at: int
    close_at: int

    @field_serializer("open_at")
    def open_time(self, open_at: int) -> str:
        return get_open_close_time(self.date, open_at).isoformat(timespec="seconds")

    @field_serializer("close_at")
    def close_time(self, close_at: int) -> str:
        return get_open_close_time(self.date, close_at).isoformat(timespec="seconds")


class Task(TaskBase, TaskStatus, TimestampSchema):
    created_by_user_id: int
    uuid: str

class TaskCreate(TaskBase):
    text: Optional[str] = Field(min_length=1, max_length=63206, examples=["Dette er første delen av task"], default=None),
    author: Annotated[
        str | None,
        Field(min_length=2,  max_length=30, examples=["forfatter"], default=None),
    ]
    test: str = Field(pattern=r"^https://www.youtube.com/watch\?v=[a-zA-Z0-9]+$", max_length=63206, examples=["vg.no"])
    yt_url: Optional[str] = Field(
            pattern=r"^https://www.youtube.com/watch\?v=[a-zA-Z0-9]+$",
            examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
        )

    answer_info: str
    answer_plaintext: str
    answer_regex: Optional[str] = None

    @field_serializer("answer_plaintext")
    def serialize_answer_plaintext(self, answer_plaintext: str) -> str:
        return enigma.encrypt_answer(answer_plaintext)

    @field_serializer("answer_regex")
    def serialize_answer_regex(self, answer_regex: str) -> str | None:
        if answer_regex:
            return enigma.encrypt_answer(answer_regex)

        return None


class TaskCreateInternal(TaskCreate):
    created_by_user_id: int


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: Optional[str]
    author: Optional[str] = Field(min_length=2, max_length=30)
    answer_info: Optional[str]
    answer_plaintext: Optional[str]
    answer_regex: Optional[str]
    open_at: Optional[int] = Field(default=9, ge=6, le=22)
    close_at: Optional[int] = Field(default=23, gt=19, le=23)
    yt_url: Optional[str] = Field(
        pattern=r"^https://www.youtube.com/watch\?v=[a-zA-Z0-9]+$",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )


class TaskUpdateInternal(TaskUpdate):
    created_by_user_id: int


class TaskRead(TaskBase, TaskStatus):
    media: Optional[List[TaskMediaRead]]
    hints: Optional[List[TaskHintRead]]


class TaskAdminRead(Task):
    media: Optional[List[TaskMediaRead]]
    hints: Optional[List[TaskHintRead]]

    @field_serializer("answer")
    def serialize_answer(self, answer: str) -> str:
        return enigma.decrypt_answer(answer)
