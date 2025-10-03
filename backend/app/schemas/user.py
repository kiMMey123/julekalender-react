import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    full_name: str
    username: str
    password: str


class UserRead(BaseModel):
    id: str
    username: str
    full_name: str
    email: str


class UserAnswerAttempt(BaseModel):
    date: datetime.date
    text: str


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
