import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_serializer, ConfigDict

from app.schemas.core import TimestampSchema, PersistentDeletion
from app.schemas.task import TaskMediaRead
from app.utils.encryption import enigma

class TaskHintBase(BaseModel):
    info: str = Field(min_length=1, max_length=63206, examples=["Dette er et hint til oppgaven"]),


class TaskHint(TaskHintBase, TimestampSchema, PersistentDeletion):
    uuid: str


class TaskHintCreate(TaskHintBase):
    hint_number: int = Field(ge=0, le=5, default=0)


class TaskHintCreateInternal(TaskHintCreate):
    date: datetime.date


class TaskHintUpdate(BaseModel):
    info: Optional[str] = Field(min_length=1, max_length=63206, examples=["Dette er et hint til oppgaven"])


class TaskHintUpdateInternal(TaskHintUpdate):
    updated_at: datetime.datetime


class TaskHintDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime.datetime


class TaskHintRead(TaskHintBase):
    hint_number: int
    media: Optional[List[TaskMediaRead]]

