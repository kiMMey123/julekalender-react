from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.core import TimestampSchema, PersistentDeletion
from app.schemas.user_task_attempt import TaskAttemptRead
from app.settings import settings


class TaskResultBase(BaseModel):
    date: date
    solved: bool = Field(default=False)
    time_solved: Optional[datetime] = None
    score: int = Field(default=0, ge=0, le=10)
    hints_used: int = Field(default=0, ge=0, le=5)
    attempts_left: int = Field(default=settings.ATTEMPTS_PER_RESET)
    attempts_reset: Optional[datetime] = None


class TaskResult(TimestampSchema, PersistentDeletion, TaskResultBase):
    id: int
    user_id: int
    task_id: int
    uuid: str


class TaskResultRead(TaskResultBase):
    id: int
    user_id: int

class TaskResultCreate(TaskResultBase):
    pass
    # model_config = ConfigDict(extra="forbid")


class TaskResultCreateInternal(TaskResultCreate):
    user_id: int
    task_id: int


class TaskResultUpdate(BaseModel):
    solved: Optional[bool] = Field(default=False)
    time_solved: Optional[datetime] = None
    score: Optional[int] = Field(default=0, ge=0, le=10)
    hints_used: Optional[int] = Field(default=0, ge=0, le=5)
    attempts_left: Optional[int]
    attempts_reset: Optional[datetime] = None


class TaskResultUpdateInternal(TaskResultUpdate):
    updated_at: datetime


class TaskResultDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime

class TaskResultWithAnswer(TaskResultRead):
    text: str
    msg: str
    attempts: Optional[List[TaskAttemptRead]] = Field(default=list)