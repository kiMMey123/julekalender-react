import datetime
from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(examples=["kari.nordmann@example.com"])]
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
