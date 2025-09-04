from typing import Annotated, List

from fastapi import Depends, APIRouter, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.database import SessionDep
from app.schemas.user import User, UserTask, UserRead

router = APIRouter()

@router.get("/users", response_model=List[UserRead])
async def get_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> list:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/users/{user_id}/", response_model=UserRead)
async def get_user_by_id(
    session: SessionDep,
    user_id: str,
) -> dict:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.get("users/{user_id}/task/")
async def get_user_task(user_id: str, session: SessionDep) -> "UserTask":
    if not await get_user_by_id(session, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    user_task = UserTask.get_or_create_daily_task(session, user_id)
    session.add(user_task)
    session.commit()
    session.refresh(user_task)
    return user_task