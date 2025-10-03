from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import session_scope
from app.schemas.user import UserCreate, UserRead
from app.models.user import User, TaskTracker, get_user_task_trackers, get_current_user

from typing import Annotated
from fastapi.params import Depends

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate):
    with session_scope() as session:
        new_user = User.create_user(user)
        try:
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
        except IntegrityError as e:
            session.rollback()
            detail = "duplicate_user"
            if "user.email" in str(e):
                detail = "duplicate_email"
            exception = HTTPException(status_code=409, detail=detail)
            raise exception
        return new_user


@router.get("/", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.get("/results/", response_model=list[TaskTracker])
async def get_my_results(
    user: Annotated[User, Depends(get_current_user)],
):
    with session_scope() as session:
        all_tasks = get_user_task_trackers(session, user.id)
        return all_tasks

@router.get("/results/today", response_model=TaskTracker)
async def get_result_today(
        user: Annotated[User, Depends(get_current_user)]
):
    with session_scope() as session:
        task = TaskTracker.get_or_create_daily_task_tracker(user_id=user.id, session=session)
        return task