import datetime
from typing import Optional, List, Annotated

from pydantic import BaseModel, Field, field_serializer, ConfigDict

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
    info: str = Field(min_length=1, max_length=63206, examples=["Dette er første delen av task"],
                                default=None)
    open_at: int = Field(ge=7, le=22)
    close_at: int = Field(gt=9, le=23)


class Task(TaskBase, TaskStatus, TimestampSchema):
    uuid: str


class TaskCreate(TaskBase):

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
    author: str = Field(min_length=2, max_length=30)
    created_by_user_id: int = Field(gt=0)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["Infotekst"], default=None),
    ]
    answer_info: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["Svartekst"], default=None),
    ]
    answer_plaintext: Annotated[
        str | None,
        Field(min_length=1, max_length=200, examples=["Svaret i plaintext"], default=None),
    ]
    answer_regex: Annotated[
        str | None,
        Field(min_length=1, max_length=200, examples=["Svaret i regex"], default=None),
    ]
    open_at: Annotated[
        int | None,
        Field(ge=7, le=22, default=9)
    ]
    close_at: Annotated[
        int | None,
        Field(ge=9, le=23, default=23)
    ]
    yt_url: Annotated[
        str | None,
        Field(
            pattern=r"^https://www.youtube.com/watch\?v=[a-zA-Z0-9]+$",
            examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
            default=None
        )
    ]
    @field_serializer("answer_plaintext")
    def serialize_answer_plaintext(self, answer_plaintext: str) -> str:
        if answer_plaintext:
            return enigma.encrypt_answer(answer_plaintext)

        return enigma.encrypt_answer(answer_plaintext)

    @field_serializer("answer_regex")
    def serialize_answer_regex(self, answer_regex: str) -> str | None:
        if answer_regex:
            return enigma.encrypt_answer(answer_regex)

        return None


class TaskUpdateInternal(TaskUpdate):
    updated_at: datetime.datetime


class TaskDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime.datetime

class TaskRead(TaskBase, TaskStatus):
    media: Optional[List[TaskMediaRead]]
    hints: Optional[List[TaskHintRead]]

    @field_serializer("open_at")
    def open_time(self, open_at: int) -> str:
        return get_open_close_time(self.date, open_at).isoformat(timespec="seconds")

    @field_serializer("close_at")
    def close_time(self, close_at: int) -> str:
        return get_open_close_time(self.date, close_at).isoformat(timespec="seconds")


class TaskAdminRead(TaskRead):
    answer_info: str
    answer_plaintext: str
    answer_regex: Optional[str] = None

    @field_serializer("answer_plaintext")
    def serialize_answer_plaintext(self, answer_plaintext: str) -> str:
        return enigma.decrypt_answer(answer_plaintext)

    @field_serializer("answer_regex")
    def serialize_answer_regex(self, answer_regex: str) -> str | None:
        if answer_regex:
            return enigma.decrypt_answer(answer_regex)

        return None
