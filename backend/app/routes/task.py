import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, and_

from app.database import session_scope
from app.models.task import Task, TaskHint
from app.models.user import User, get_current_user
from app.models.user_task_result import TaskResult
from app.schemas.task import TaskUserRead
from app.schemas.user import UserAnswerReply

router = APIRouter()


async def get_current_task():
    with session_scope() as session:
        task = Task.get_task(session)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.status == "active":
        raise HTTPException(status_code=403, detail="No active task")
    return task


@router.get("/{date}", response_model=TaskUserRead)
async def get_task_by_date(date: datetime.date = datetime.date.today()):
    with session_scope() as session:
        if task := Task.get_task(session=session, date=date):
            return TaskUserRead(**task.get_admin_task().model_dump())
        raise HTTPException(404, "Task not found")


@router.post("/answer", response_model=UserAnswerReply)
async def answer_task(
        user: Annotated[User, Depends(get_current_user)],
        task: Annotated[Task, Depends(get_current_task)],
        answer: str
):
    try:
        with session_scope() as session:
            task_tracker = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
            answer_txt = answer.strip().lower()
            attempt_result = task_tracker.check_attempt(text=answer_txt, task=task, session=session)

            if attempt_result == "duplicate":
                raise HTTPException(status_code=400, detail={
                    "type": "duplicate",
                    "message": "input is a duplicate from previous attempt",
                    "input": answer
                })
            elif attempt_result == "no_attempts":
                raise HTTPException(status_code=429,
                                    detail={"type": "attempt", "time": task_tracker.attempts_reset.isoformat()})
            else:
                answer_reply = UserAnswerReply(message=attempt_result, text=answer_txt, **task_tracker.model_dump())
                return answer_reply

    except IntegrityError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/hint", response_model=list[Optional[TaskHint]])
async def get_user_hint(
        user: Annotated[User, Depends(get_current_user)],
        task: Annotated[Task, Depends(get_current_task)]
):
    with session_scope() as session:
        task_tracker = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
        if task_tracker.solved:
            return task.hints

        hints = session.exec(
            select(TaskHint)
            .where(and_(
                TaskHint.date == task_tracker.date,
                TaskHint.hint_number <= task_tracker.hints_used
            ))
        ).all()

        return hints


@router.post("/hint/unlock", status_code=204)
async def unlock_user_hint(
        user: Annotated[User, Depends(get_current_user)],
        task: Annotated[Task, Depends(get_current_task)],
):
    with session_scope() as session:
        task_tracker = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
        if task_tracker.solved:
            raise HTTPException(status_code=400, detail="Task is already solved")
        if task_tracker.hints_used >= len(task.hints):
            raise HTTPException(status_code=400, detail={"type": "hint", "message": "no hints left"})
        else:
            task_tracker.hints_used += 1
            session.add(task_tracker)
            session.commit()
