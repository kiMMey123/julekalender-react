import datetime
import re
from typing import Annotated, cast, Optional, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from fastcrud.exceptions.http_exceptions import BadRequestException
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks_hints import crud_tasks_hints
from app.crud.crud_tasks import crud_tasks
from app.crud.crud_tasks_media import crud_tasks_media
from app.crud.crud_users_attempts import crud_users_attempts
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.models.task_media import TaskMedia
from app.schemas.task import TaskRead, TaskAdminRead, TaskCreate, TaskCreateInternal, TaskUpdate, TaskMediaRead
from app.schemas.task_hint import TaskHint, TaskHintRead, TaskHintCreate
from app.schemas.user_task_attempt import TaskAttemptCreateInternal, TaskAttemptRead
from app.settings import settings
from app.utils.input import string_washer
from app.utils.user_utils import get_current_user, get_or_create_task_result, get_current_superuser

router = APIRouter()


@router.post("/{date}")
async def post_task_hint(
        user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
        hint: TaskHintCreate,
        date: datetime.date,
):
    if not 0 <= hint.hint_number <= 5:
        raise BadRequestException()

    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if await crud_tasks_hints.exists(db=db, task_id=db_task["id"], is_deleted=False, hint_number=hint.hint_number):
        raise HTTPException(status_code=400, detail=f'Hint number {hint.hint_number} already exists on {date}')

    hint_internal = hint.model_dump()
    hint_internal["date"] = date

    created_hint = await crud_tasks_hints.create(db=db, object=hint_internal)
    task_read = await crud_tasks_hints.get(db=db, id=created_hint.id, schema_to_select=TaskHintRead)

    if task_read is None:
        raise HTTPException(status_code=500, detail="Server could not process request")

    return cast(TaskRead, task_read)


@router.get("/{date}/{hint_number}", response_model=TaskHintRead)
async def get_task_hint(
        date: datetime.date,
        hint_number: int,
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
):
    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if TaskRead(**db_task).status == "locked" and not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Task is locked")

    db_hint = await crud_tasks_hints.get(db=db, task_id=db_task["id"], hint_number=hint_number, is_deleted=False, schema_to_select=TaskHintRead)

    if not db_hint:
        raise HTTPException(status_code=404, detail="Hint not found")

    if user["is_admin"] or TaskRead(**db_task).status == "expired":
        return TaskHintRead(**db_hint)
    else:
        user_results = await get_or_create_task_result(db=db, user_id=user["id"], task=db_task)
        if user_results.hints_used <= hint_number:
            return TaskHintRead(**db_hint)
        else:
            raise HTTPException(status_code=403, detail="Hint is not available")