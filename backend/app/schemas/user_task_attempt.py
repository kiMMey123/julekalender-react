from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.core import TimestampSchema, PersistentDeletion


class TaskAttemptBase(BaseModel):
    date: date
    text: str


class TaskAttempt(TimestampSchema, PersistentDeletion, TaskAttemptBase):
    msg: str
    id: int
    user_id: int
    task_id: int
    uuid: str


class TaskAttemptRead(TaskAttemptBase):
    msg: str
    user_id: int


class TaskAttemptCreate(TaskAttemptBase):
    model_config = ConfigDict(extra="forbid")


class TaskAttemptCreateInternal(TaskAttemptCreate):
    msg: str
    user_id: int
    task_id: int
    task_result_id: int


class TaskAttemptUpdate(TaskAttemptCreate):
    pass


class TaskAttemptUpdateInternal(TaskAttemptUpdate):
    updated_at: datetime


class TaskAttemptDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
