from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.database import SessionDep
from app.schemas.user import User, UserCreate, UserTaskUpdate, UserTask, UserRead, get_user_tasks

from app.utils.security import oauth2_scheme, SECRET_KEY, ALGORITHM, TokenData, decode_payload
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

async def get_current_user(session:SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_data := decode_payload(token):
        user = User.get_user_by_username_or_email(session, token_data.username)
        if not user:
            raise credentials_exception
        return user
    raise credentials_exception

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
    task = UserTask.get_or_create_daily_task(session=session, user_id=user.id)
    return task