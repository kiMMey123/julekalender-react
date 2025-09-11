import datetime

import pydantic
from sqlmodel import SQLModel, Field, Relationship, select
from typing import Optional, List


from app.utils.security import generate_uid


class Task(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, default=datetime.date.today(), unique=True)
    points: int = Field(default=10)
    text: str = Field(nullable=False)
    yt_url: Optional[str] = Field(nullable=True)
    answer: "TaskAnswer" = Relationship(back_populates="task", cascade_delete=True)
    hints: List["TaskHint"] = Relationship(back_populates="task", cascade_delete=True)

    @classmethod
    def get_active_task(cls, session) -> Optional["Task"]:
        today = datetime.date.today()
        task = session.query(cls).filter_by(date=today).first()
        return task

class TaskCreate(pydantic.BaseModel):
    date: datetime.date
    points: int = pydantic.Field(default=10)
    text: str
    yt_url: Optional[str] = Field(nullable=True)
    author: Optional[str] = Field(nullable=True)
    answer: str

class TaskHint(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, unique=True, foreign_key="task.date")
    hint_number: int = Field(primary_key=True, unique=True, nullable=False)
    points: int = Field(default=7)
    task: Task = Relationship(back_populates="hints")

class TaskAnswer(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, unique=True, foreign_key="task.date")
    answer: str = Field(nullable=False)
    task: Task = Relationship(back_populates="answer")

class UserAnswer(pydantic.BaseModel):
    date: datetime.date
    answer: str

class UserAnswerReply(UserAnswer):
    pass