from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_get_db
from app.schemas.user import UserCreate, UserRead
from app.models.user import User, get_user_task_trackers, get_current_user
from app.crud.crud_users import crud_users
from app.models.task_tracker import TaskResult

from typing import Annotated
from fastapi.params import Depends

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(
        request: Request,
        user: UserCreate,
        db: Annotated[AsyncSession, Depends(async_get_db)]
):
    email_row = await crud_users.exists(db=db, email=user.email)
    if email_row:
        raise DuplicateValueException("Email is already registered")

    username_row = await crud_users.exists(db=db, username=user.username)
    if username_row:
        raise DuplicateValueException("Username not available")


@router.get("/", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.get("/results/", response_model=list[TaskResult])
async def get_my_results(
    user: Annotated[User, Depends(get_current_user)],
):
    with session_scope() as session:
        all_tasks = get_user_task_trackers(session, user.id)
        return all_tasks

@router.get("/results/today", response_model=TaskResult)
async def get_result_today(
        user: Annotated[User, Depends(get_current_user)]
):
    with session_scope() as session:
        task = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
        return task