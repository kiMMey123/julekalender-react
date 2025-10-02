import datetime
from typing import Annotated, List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette import status

from app.database import SessionDep, session_scope
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskAnswer, TaskHint, TaskHintCreate, create_or_update_task, \
    TaskAdminRead
from app.schemas.user import User, TaskTracker, UserRead
from app.utils.encryption import enigma

router = APIRouter()

@router.get("/{date}/", response_model=TaskAdminRead)
async def get_task(date: datetime.date) -> dict:
    with session_scope() as session:
        if task := session.exec(select(Task).where(Task.date == date)).first():
            return task.to_admin_dict()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("/{date}/", response_model=TaskAdminRead)
async def create_task(date: datetime.date, new_task: TaskCreate) -> dict:
    if new_task.open_time >= new_task.close_time:
        raise HTTPException(status_code=422, detail="close time must be after open time")

    return create_or_update_task(new_task, date)


@router.patch("/{date}/", response_model=TaskAdminRead)
async def update_task(date: datetime.date, updated_task: TaskUpdate) -> dict:
    return create_or_update_task(updated_task, date)

@router.delete("/{date}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(date: str = datetime.date.today()):
    with session_scope() as session:
        if task := session.exec(select(Task).where(Task.date == date)).first():
            session.delete(task)
            session.commit()
        else:
            raise HTTPException(status_code=404, detail="Task not found")

@router.get("/{date}/hint/")
async def get_task_hint(date: datetime.date = datetime.date.today()):
    with session_scope() as session:
        task = session.exec(select(Task).where(Task.date == date)).first()
        if task:
            return task.hints
        else:
            raise HTTPException(status_code=404, detail="Task not found")

@router.post("/{date}/hint/", response_model=TaskHint)
async def add_task_hint(hint: TaskHintCreate, date: datetime.date):
    with session_scope() as session:
        task = session.exec(select(Task).where(Task.date == date)).first()
        if task:
            if len(task.hints) >= 5:
                raise HTTPException(status_code=400, detail="Too many hints")
            number_of_hints = len(task.hints) + 1
            new_hint = hint.model_dump()
            new_hint["date"] = date
            new_hint["hint_number"] = number_of_hints
            session.add(TaskHint(**new_hint))
            session.commit()
            return TaskHint(**new_hint)
        else:
            raise HTTPException(status_code=404, detail="Task not found")
