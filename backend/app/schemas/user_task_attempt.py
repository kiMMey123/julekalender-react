import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.core import TimestampSchema, PersistentDeletion


class TaskAttemptBase(BaseModel):
    text: str


class TaskAttempt(TimestampSchema, PersistentDeletion, TaskAttemptBase):
    msg: str
    id: int
    user_id: int
    task_id: int
    uuid: str


class TaskAttemptRead(TaskAttemptBase):
    msg: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class TaskAttemptCreate(TaskAttemptBase):
    model_config = ConfigDict(extra="forbid")


class TaskAttemptCreateInternal(TaskAttemptCreate):
    date: datetime.date = Field(default_factory=datetime.date.today)
    msg: str
    user_id: int
    task_id: int
    task_result_id: int
    # created_at: datetime.datetime


class TaskAttemptUpdate(TaskAttemptCreate):
    pass


class TaskAttemptUpdateInternal(TaskAttemptUpdate):
    updated_at: datetime.datetime


class TaskAttemptDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime.datetime
