from datetime import date

from fastapi import APIRouter, HTTPException, Request
from fastcrud.exceptions.http_exceptions import DuplicateValueException, NotFoundException, ForbiddenException
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.utils.task_utils import get_current_task
from app.schemas.task import Task, TaskRead
from app.schemas.user import UserCreate, UserRead, UserCreateInternal, UserUpdate
from app.models.user import User
from app.utils.user_utils import get_current_user, get_or_create_task_result, get_current_superuser
from app.crud.crud_users import crud_users
from app.models.user_task_result import TaskResult

from typing import Annotated, cast, Any
from fastapi.params import Depends

from app.schemas.user_task_result import TaskResultRead, TaskResultCreate, TaskResultCreateInternal
from app.utils.security import get_password_hash

router = APIRouter()

@router.post("", response_model=UserRead)
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

@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return current_user

@router.get("", response_model=PaginatedListResponse[UserRead])
async def read_users(
        request: Request,
        user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
        page: int = 1, items_per_page: int = 10
) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.patch("/{username}", response_model=UserRead)
async def update_user(
        request: Request,
        username: str,
        values: UserUpdate,
        db: Annotated[AsyncSession, Depends(async_get_db)],
        current_user: Annotated[dict, Depends(get_current_user)]
):
    db_user = await crud_users.get(db=db, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    if db_user["username"] != current_user["username"]:
        raise ForbiddenException()

    if values.email is not None and values.email != db_user["email"]:
        if await crud_users.exists(db=db, email=values.email):
            raise DuplicateValueException("Email is already registered")

    if values.username is not None and values.username != db_user["username"]:
        if await crud_users.exists(db=db, username=values.username):
            raise DuplicateValueException("Username not available")

    await crud_users.update(db=db, object=values, username=username)
    updated_user = await crud_users.get(db=db, username=username, is_deleted=False)
    return updated_user