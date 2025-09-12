from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import SessionDep
from app.schemas.user import User, UserCreate, UserTask, UserRead, get_user_tasks, get_current_user

from typing import Annotated
from fastapi.params import Depends

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    new_user = User.create_user(user)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except IntegrityError as e:
        session.rollback()
        detail = "duplicate_user"
        exception = HTTPException(status_code=409, detail=detail)
        if "user.email" in str(e):
            detail = "duplicate_email"
        raise exception
    return new_user


@router.get("/", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.get("/tasks/", response_model=list[UserTask])
async def get_my_tasks(
    session:SessionDep,
    user: Annotated[User, Depends(get_current_user)],
):
    all_tasks = get_user_tasks(session, user.id)
    return all_tasks

@router.get("/tasks/today", response_model=UserTask)
async def get_todays_tasks(
        user: Annotated[User, Depends(get_current_user)],
        session: SessionDep,
):
    task = UserTask.get_or_create_daily_task(user_id=user.id, session=session)
    return task