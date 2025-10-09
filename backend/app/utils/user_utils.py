import datetime
from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users import crud_users
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.schemas.task import TaskRead
from app.schemas.user import UserRead
from app.schemas.user_task_result import TaskResultRead, TaskResultCreateInternal
from app.utils.security import oauth2_scheme, decode_payload


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(async_get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_data := decode_payload(token):
        if "@" in token_data.username:
            user = await crud_users.get(db=db, email=token_data.username, is_deleted=False)
        else:
            user = await crud_users.get(db=db, username=token_data.username, is_deleted=False)

        if user:
            if hasattr(user, 'model_dump'):
                return user.model_dump()
            else:
                return user

    raise credentials_exception


async def get_or_create_task_result(db: AsyncSession, user_id: int, task_id: int,
                                    date: datetime.date = datetime.date.today()) -> TaskResultRead:

    db_task = await crud_tasks.exists(db=db, id=task_id, is_deleted=False, schema_to_select=TaskRead)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task_result = await crud_users_results.get(db=db, user_id=user_id, task_id=task_id, is_deleted=False,
                                               schema_to_select=TaskResultRead)

    if not task_result:
        if date == datetime.date.today():
            new_result = TaskResultCreateInternal(
                date=date,
                user_id=user_id,
                task_id=task_id
            )
            created_result = await crud_users_results.create(db=db, object=new_result)
            result = await crud_users_results.get(db=db, id=created_result.id, schema_to_select=TaskResultRead)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to create task result",
                )
            return TaskResultRead(**result)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task result not found",
            )
    else:
        return TaskResultRead(**task_result)

async def check_user_answer_attempt(db: AsyncSession, user_id: int, attempt_id: int, attempt_date: datetime.date):
    pass