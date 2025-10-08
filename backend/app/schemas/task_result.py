from datetime import date, datetime

from pydantic import BaseModel, Field, HttpUrl, field_serializer, ConfigDict
from typing import Optional, List, TYPE_CHECKING, Annotated

from app.schemas.core import TimestampSchema, PersistentDeletion
from app.settings import ATTEMPTS_PER_RESET
from app.utils.encryption import enigma
from app.utils.time import get_open_close_time

class TaskResultBase(BaseModel):
    date: date
    solved: bool = Field(default=False)
    time_solved: Optional[datetime] = None
    score: int = Field(default=0, ge=0, le=10)
    hints_used: int = Field(default=0, ge=0, le=5)
    attempts_left: int = Field(default=ATTEMPTS_PER_RESET)
    attempts_reset: Optional[datetime] = None

class TaskResult(TimestampSchema, PersistentDeletion, TaskResultBase):
    id: int
    user_id: int
    uuid: str

class TaskResultRead(TaskResultBase):
    id: int

class UserAnswerReply(UserAnswerAttempt):
    message: str
    user_id: str
    solved: bool
    time_solved: Optional[datetime.datetime]
    score: int
    hints_used: int
    attempts_left: int
    attempts_reset: Optional[datetime.datetime]
    attempts: list[str]
