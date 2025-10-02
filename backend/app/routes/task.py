import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, and_

from app.database import SessionDep, session_scope
from app.schemas.task import Task, TaskHint, TaskUserRead
from app.schemas.user import User, TaskTracker, UserAnswerAttempt, UserAnswerReply, get_current_user

from typing import Annotated, Optional
from fastapi.params import Depends

router = APIRouter()

async def get_current_task(session: SessionDep):
    task = Task.get_task(session)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.status == "active":
        raise HTTPException(status_code=403, detail="No active task")
    return task

@router.get("/{date}", response_model=TaskUserRead)
async def get_task_by_date(date: datetime.date):
    pass

@router.post("/answer", response_model=UserAnswerReply)
async def answer_task(
    user: Annotated[User, Depends(get_current_user)],
    task: Annotated[Task, Depends(get_current_task)],
    answer: str
):
    try:
        with session_scope() as session:
            task_tracker = TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session)
            answer_txt = answer.strip().lower()
            attempt_result = task_tracker.check_attempt(text=answer_txt, task=task, session=session)

            if attempt_result == "duplicate":
                raise HTTPException(status_code=400, detail={
                    "type": "duplicate",
                    "message": "input is a duplicate from previous attempt",
                    "input": answer
                })
            elif attempt_result == "no_attempts":
                raise HTTPException(status_code=429, detail={"type": "attempt", "time": task_tracker.attempts_reset.isoformat()})
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
        task_tracker = TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session)
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
        task_tracker = TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session)
        if task_tracker.solved:
            raise HTTPException(status_code=400, detail="Task is already solved")
        if task_tracker.hints_used >= len(task.hints):
            raise HTTPException(status_code=400, detail={"type": "hint", "message": "no hints left"})
        else:
            task_tracker.hints_used += 1
            session.add(task_tracker)
            session.commit()

