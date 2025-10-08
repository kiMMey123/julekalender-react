from datetime import date

from fastapi import APIRouter, HTTPException, Request
from fastcrud.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_users_results import crud_task_results
from app.database import async_get_db
from app.utils.task_utils import get_current_task
from app.schemas.task import Task, TaskRead
from app.schemas.user import UserCreate, UserRead, UserCreateInternal
from app.models.user import User
from app.utils.user_utils import get_current_user
from app.crud.crud_users import crud_users
from app.models.user_task_result import TaskResult

from typing import Annotated, cast
from fastapi.params import Depends

from app.schemas.user_task_result import TaskResultRead, TaskResultCreate, TaskResultCreateInternal
from app.utils.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(
        request: Request,
        user: UserCreate,
        db: Annotated[AsyncSession, Depends(async_get_db)]
):
    if await crud_users.exists(db=db, email=user.email):
        raise DuplicateValueException("Email is already registered")

    username_row = await crud_users.exists(db=db, username=user.username)
    if username_row:
        raise DuplicateValueException("Username not available")

    user_internal_dict = user.model_dump()
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal)

    user_read = await crud_users.get(db=db, id=created_user.id, schema_to_select=UserRead)
    if user_read is None:
        raise NotFoundException("Created user not found")

    return cast(UserRead, user_read)

@router.get("/", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.get("/results/", response_model=list[TaskResultRead])
async def get_my_results(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    user_results = await crud_task_results.get_multi(
        db=db,
        limit=30,
        user_id=user["id"],
        schema_to_select=TaskResultRead
    )
    return user_results["data"]

@router.get("/results/today", response_model=TaskResultRead)
async def get_result_today(
        user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)]
):
    task = await get_current_task(db=db)

    result = await crud_task_results.get(db=db, user_id=user["id"], task_id=task["id"], schema_to_select=TaskResultRead)
    print(result)
    if not result:
        new_result = TaskResultCreateInternal(
            date=task["date"],
            user_id=user["id"],
            task_id=task["id"],
        )

        created_result = await crud_task_results.create(db=db, object=new_result)
        result = await crud_task_results.get(db=db, id=created_result.id, schema_to_select=TaskResultRead)

    return cast(TaskResultRead, result)