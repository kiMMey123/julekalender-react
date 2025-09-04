from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from app.database import SessionDep
from app.schemas.user import User, UserCreate, UserTaskUpdate, UserTask, UserRead

from app.utils.security import oauth2_scheme
from typing import Annotated
from fastapi.params import Depends

router = APIRouter()


def fake_decode_token(token):
    return User.create_user(
        email="john@example.com", username=token + "fakedecoded"
    )

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

async def get_current_user(session:SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = User.get_user_by_username_or_email(session, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.get("/", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.get("/task/", response_model=UserTask)
async def get_my_tasks(
    token: Annotated[User, Depends(get_current_user)],
):
    return {"token": token}

@router.get("/task/today/", response_model=UserTask)
async def get_todays_tasks(
        token: Annotated[User, Depends(get_current_user)],
        session: SessionDep,
):
    task = UserTask.get_or_create_daily_task(session, token.id)
    return task