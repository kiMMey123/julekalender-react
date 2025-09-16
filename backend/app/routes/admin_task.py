import datetime
from typing import Annotated, List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from starlette import status

from app.database import SessionDep, session_scope
from app.routes.tests import enigma
from app.schemas.task import Task, TaskCreate, TaskAnswer, TaskHint, TaskHintCreate
from app.schemas.user import User, TaskTracker, UserRead
from app.utils.encryption import enigma

router = APIRouter()

@router.post("/{date}/", response_model=Task)
async def create_task(date: datetime.date, new_task: TaskCreate) -> Task:
    new_task_dict: dict =  new_task.to_task_dict()

    answer_encrypted = enigma.encrypt_answer(txt=new_task_dict.pop("answer"))
    answer = TaskAnswer(date=date, text=answer_encrypted)
    created_task = Task(date=date, **new_task_dict)

    with session_scope() as session:
        session.add(created_task)
        session.add(answer)
        session.commit()
        session.refresh(created_task)
    return created_task

@router.delete("/{date}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(date: str):
    with session_scope() as session:
        task = session.exec(select(Task).where(Task.date == date)).first()
        print(task)
        if task:
            session.delete(task)
            session.commit()
        else:
            raise HTTPException(status_code=404, detail="Task not found")

@router.get("/{date}/hint/")
async def get_task_hint(date: datetime.date):
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
            print(task.hints, len(task.hints))
            if len(task.hints) >= 5:
                raise HTTPException(status_code=400, detail="Too many hints")
            number_of_hints = len(task.hints) + 1
            print(number_of_hints)
            new_hint = hint.model_dump()
            new_hint["date"] = date
            new_hint["hint_number"] = number_of_hints
            session.add(TaskHint(**new_hint))
            session.commit()
            return TaskHint(**new_hint)
        else:
            raise HTTPException(status_code=404, detail="Task not found")







@router.get("/today")
async def get_active_task(session: SessionDep) -> dict:
    task = Task.get_active_task(session)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_json = task.model_dump()
    if task.answer:
        task_json["answer"] = enigma.decrypt_answer(task.answer.text)

    return task_json
