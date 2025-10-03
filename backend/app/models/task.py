import datetime
from typing import List, Optional, Union

from fastapi import HTTPException
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, Relationship, Session, select

from app.database import session_scope
from app.models.media import TaskMedia
from app.schemas.task import TaskAdminRead
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.encryption import enigma
from app.utils.time import get_open_close_time


class Task(SQLModel, table=True):
    date: datetime.date = Field(default=datetime.date.today(), primary_key=True, unique=True)
    open_time: datetime.datetime = Field(nullable=False)
    close_time: datetime.datetime = Field(nullable=False)
    info: str = Field(nullable=False)
    answer: "TaskAnswer" = Relationship(back_populates="task", cascade_delete=True)
    hints: List["TaskHint"] = Relationship(back_populates="task", cascade_delete=True)
    media: List["TaskMedia"] = Relationship(back_populates="task", cascade_delete=True)

    @classmethod
    def get_task(cls, session: Session, date: datetime.date = datetime.date.today()) -> Optional["Task"]:
        task = session.exec(select(cls).where(cls.date == date)).first()
        return task

    def get_admin_task(self) -> TaskAdminRead:
        admin_task_dict = self.model_dump()
        admin_task_dict["status"] = self.status

        if self.answer:
            admin_task_dict["answer_plaintext"] = enigma.decrypt_answer(self.answer.text)
            admin_task_dict["answer"] = self.answer.model_dump()

        admin_task_dict["media"] = self.media
        admin_task_dict["hints"] = self.hints

        return TaskAdminRead(**admin_task_dict)

    def check_answer(self, text) -> bool:
        return enigma.compare_answer(text, self.answer.text)

    @property
    def status(self) -> str:
        now = datetime.datetime.now()
        if self.open_time > now:
            return "closed"
        elif self.open_time < now < self.close_time:
            return "open"
        else:
            return "expired"


class TaskHint(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, foreign_key="task.date")
    info: Optional[str] = Field(nullable=True)
    hint_number: int = Field(primary_key=True, nullable=False, le=5)
    task: Task = Relationship(back_populates="hints")

    __table_args__ = (
        UniqueConstraint("date", "hint_number"),
    )


class TaskAnswer(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, unique=True, foreign_key="task.date")
    text: str = Field(nullable=False)
    task: Task = Relationship(back_populates="answer")
    yt_url: Optional[str]


def create_or_update_task(data: Union[TaskCreate, TaskUpdate], date) -> TaskAdminRead:
    try:
        with session_scope() as session:
            task_dict = {k: v for k, v in data.model_dump().items() if v is not None}

            for k, v in task_dict.items():
                match k:
                    case "open_time" | "close_time":
                        task_dict[k] = get_open_close_time(date, v)
                    case "answer":
                        task_dict[k] = enigma.encrypt_answer(task_dict.get("answer"))
                    case "yt_url":
                        task_dict[k] = task_dict.get("yt_url").unicode_string()

            answer_dict = {
                "text": task_dict.pop("answer", None),
                "yt_url": task_dict.pop("yt_url", None)
            }

            if task := Task.get_task(session, date):
                if task.status != "closed":
                    raise HTTPException(status_code=403, detail="cannot edit open or expired task")
                for k, v in task_dict.items():
                    setattr(task, k, v)
                answer = task.answer
                for k, v in answer_dict.items():
                    if v is not None:
                        setattr(answer, k, v)

            else:
                task = Task(date=date, **task_dict)
                answer = TaskAnswer(date=date, **answer_dict)

            session.add(task)
            session.add(answer)
            session.commit()
            session.refresh(answer)
            session.refresh(task)
            return task.get_admin_task()

    except IntegrityError as e:
        raise HTTPException(status_code=422, detail=str(e))


TaskAdminRead.model_rebuild()
