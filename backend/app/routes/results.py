from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Request
from fastcrud.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.utils.task_utils import get_current_task
from app.schemas.task import Task, TaskRead
from app.schemas.user import UserCreate, UserRead, UserCreateInternal
from app.models.user_task_result import TaskResult
from app.models.user import User
from app.utils.user_utils import get_current_user, get_or_create_task_result
from app.crud.crud_users import crud_users
from app.models.user_task_result import TaskResult

from typing import Annotated, cast, Optional, List
from fastapi.params import Depends

from app.schemas.user_task_result import TaskResultRead, TaskResultCreate, TaskResultCreateInternal
from app.utils.security import get_password_hash

router = APIRouter()

# @router.get("/scoreboard/today")
# def get_daily_scoreboard(
#         db: Annotated[AsyncSession, Depends(async_get_db)],
# ):
#     today = date.today()
#     results =

@router.get("/me", response_model=Optional[List[TaskResultRead]])
async def get_my_results(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    user_results = await crud_users_results.get_multi(
        db=db,
        limit=30,
        user_id=user["id"],
        schema_to_select=TaskResultRead
    )
    return user_results["data"]


@router.get("/me/{date}", response_model=TaskResultRead)
async def get_result(
        user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
        date: date
):
    db_task = await crud_tasks.get(db=db, date=date)

    result = await get_or_create_task_result(db=db, user_id=user["id"], task=db_task)

    if result is not None:
        return result
    else:
        raise HTTPException(status_code=404, detail="User result not found")

@router.get("/scoreboard")
async def get_scoreboard(
        # user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    query = select(
        TaskResult.user_id,
        func.sum(TaskResult.score).label('total_score'),
        func.sum(TaskResult.hints_used).label('total_hints_used')
    ).group_by(TaskResult.user_id)

    result = await db.execute(query)

    return [
        {
            "user_id": row.user_id,
            "total_score": row.total_score,
            "total_hints_used": row.total_hints_used
        }
        for row in result.all()
    ]
    return results