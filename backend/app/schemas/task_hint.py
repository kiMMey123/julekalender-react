import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_serializer, ConfigDict

from app.schemas.core import TimestampSchema
from app.utils.encryption import enigma

class TaskMediaRead(BaseModel):
    file_name: str
    description: str
    media_type: str

class TaskHintBase(BaseModel):
    date: datetime.date
    info: str = Field(min_length=1, max_length=63206, examples=["Dette er et hint til oppgaven"]),


class TaskHint(TaskHintBase, TimestampSchema):
    uuid: str


class TaskHintCreate(TaskHintBase):
    pass

class TaskHintCreateInternal(TaskHintCreate):
    pass


class TaskHintUpdate(BaseModel):
    info: Optional[str] = Field(min_length=1, max_length=63206, examples=["Dette er et hint til oppgaven"])


class TaskHintUpdateInternal(TaskHintUpdate):
    updated_at: datetime.datetime


class TaskHintDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime.datetime


class TaskHintRead(TaskHintBase):
    media: Optional[List[TaskMediaRead]]

