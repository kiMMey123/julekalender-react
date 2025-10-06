from typing import Annotated, List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from starlette import status

from app.database import session_scope
from app.schemas.task import TaskCreate
from app.models.task import Task, TaskAnswer
from app.schemas.user import UserRead
from app.models.user import User
from app.models.task_tracker import TaskResult
from app.utils.encryption import enigma

router = APIRouter()

@router.get("/", response_model=List[UserRead])
async def get_users(
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> list:
    with session_scope() as session:
        users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/{user_id}/", response_model=UserRead)
async def get_user_by_id(
    user_id: str,
) -> User:
    with session_scope() as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

@router.get("/{user_id}/task/")
async def get_user_task(user_id: str) -> "TaskResult":
    if not await get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    user_task = TaskResult.get_or_create_daily_task_tracker(user_id)
    with session_scope() as session:
        session.add(user_task)
        session.commit()
        session.refresh(user_task)
    return user_task


