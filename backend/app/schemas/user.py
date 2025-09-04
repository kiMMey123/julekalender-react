from datetime import datetime, date, timedelta
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship, select, or_

from app.database import SessionDep, get_session
from app.utils.security import fake_hash_password, generate_user_id

class User(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True, default=generate_user_id())
    username: str = Field(unique=True)
    full_name: str = Field()
    email: str = Field(unique=True)
    email_verified: Optional[bool] = Field(default=False)
    hashed_password: str = Field(max_length=64)

    # Relationship to UserTask - fixed relationship name
    tasks: List["UserTask"] = Relationship(back_populates="user", cascade_delete=True)

    @classmethod
    def create_user(cls, user: "UserCreate") -> "User":
        user_dict = user.model_dump()
        hashed_password = fake_hash_password(user_dict.pop("password"))
        user_dict["hashed_password"] = hashed_password
        return cls(**user_dict)

    @classmethod
    def get_user_by_username_or_email(cls, session:SessionDep, username: str) -> Optional["User"]:
        if user := (
                session.exec(
                    select(cls)
                    .where(or_(
                        cls.username == username,
                cls.email == username)))
                .first()):
            return user
        return None

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

class UserTask(SQLModel, table=True):
    day: date = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    solved: bool = Field(default=False)
    time_solved: Optional[datetime] = Field(default=None)
    score: int = Field(default=0)
    hints_used: int = Field(default=0)
    attempts_left: int = Field(default=5)
    attempts_reset: Optional[datetime] = Field(default=None)

    user: User = Relationship(back_populates="tasks")

    @classmethod
    def get_or_create_daily_task(cls, session, user_id: str, task_day: date = None):
        if task_day is None:
            task_day = date.today()

        task = session.query(cls).filter_by(user_id=user_id, day=task_day).first()
        if not task:
            task = cls(user_id=user_id, day=task_day)
        return task

    __table_args__ = (
        UniqueConstraint("day", "user_id"),
    )


class UserTaskCreate(BaseModel):
    day: date
    user_id: int
    attempts_left: int = 5


class UserTaskUpdate(BaseModel):
    solved: Optional[bool] = None
    time_solved: Optional[datetime] = None
    score: Optional[int] = None
    hints_used: Optional[int] = None
    attempts_left: Optional[int] = None
    attempts_reset: Optional[datetime] = None