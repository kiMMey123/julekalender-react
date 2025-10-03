import datetime
from typing import Optional, List, Annotated

from fastapi import HTTPException
from fastapi.params import Depends

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlalchemy.orm import attributes
from sqlmodel import SQLModel, Field, Relationship, select, or_, Session
from starlette import status

from app.database import session_scope
from app.models.task import Task
from app.schemas.user import UserCreate
from app.settings import ATTEMPTS_PER_RESET, SCORES_PER_HINT_USED
from app.utils.input import string_washer
from app.utils.security import generate_uid, get_password_hash, oauth2_scheme, decode_payload


class User(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True, default=generate_uid())
    username: str = Field(unique=True)
    full_name: str = Field()
    email: str = Field(unique=True)
    email_verified: Optional[bool] = Field(default=False)
    hashed_password: str = Field(max_length=64)
    results: List["TaskTracker"] = Relationship(back_populates="user", cascade_delete=True)

    @classmethod
    def create_user(cls, user: "UserCreate") -> "User":
        user_dict = user.model_dump()
        hashed_password = get_password_hash(password=user_dict.pop("password"))
        user_dict["hashed_password"] = hashed_password
        return cls(**user_dict)

    @classmethod
    def get_user_by_username_or_email(cls, username: str) -> Optional["User"]:
        with session_scope() as session:
            if user := (
                    session.exec(
                        select(cls)
                                .where(or_(
                            cls.username == username,
                            cls.email == username)))
                            .first()):
                return user
        return None


class TaskTracker(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    solved: bool = Field(default=False)
    time_solved: Optional[datetime.datetime] = Field(default=None)
    score: int = Field(default=0)
    hints_used: int = Field(default=0)
    attempts_left: int = Field(default=ATTEMPTS_PER_RESET)
    attempts_reset: Optional[datetime.datetime] = Field(default=None)
    attempts: list[str] = Field(default=[], sa_column=Column(JSON))
    user: User = Relationship(back_populates="results")

    __table_args__ = (
        UniqueConstraint("date", "user_id"),
    )

    @classmethod
    def get_or_create_daily_task_tracker(cls, user_id: str, session: Session,
                                         task_date: datetime.date = datetime.date.today()):
        task = session.exec(select(cls).filter_by(user_id=user_id, date=task_date)).first()
        if not task:
            task = cls(user_id=user_id, date=task_date)
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    def check_attempt(self, text: str, task: Task, session) -> str:
        text = string_washer(text)
        message = "incorrect"

        if self.solved:
            message = "solved"
        elif text in self.attempts:
            message = "duplicate"
        elif self.attempts_left <= 0:
            if self.attempts_reset is not None:
                if datetime.datetime.now() >= self.attempts_reset:
                    self.attempts_left = ATTEMPTS_PER_RESET
                    self.attempts_reset = None
                    message = self.check_attempt(text, task, session)
                else:
                    message = "no_attempts"

        else:
            self.attempts.append(text)
            self.attempts_left -= 1

            if self.attempts_left <= 0:
                self.attempts_reset = datetime.datetime.now() + datetime.timedelta(seconds=30)

            attributes.flag_modified(self, 'attempts')

            if task.check_answer(text=text):
                self.solved = True
                self.time_solved = datetime.datetime.now()
                self.score = SCORES_PER_HINT_USED[self.hints_used]
                message = "correct"

        if message not in ["solved", "duplicate", "no_attempts"]:
            session.add(self)
            session.commit()
            session.refresh(self)

        return message


def get_user_task_trackers(session, user):
    trackers = session.query(TaskTracker).filter_by(user_id=user).all()
    return trackers


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_data := decode_payload(token):
        user = User.get_user_by_username_or_email(token_data.username)
        if not user:
            raise credentials_exception
        return user
    raise credentials_exception
