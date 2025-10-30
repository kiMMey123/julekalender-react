import datetime
import re
from typing import Annotated, cast, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks_hints import crud_tasks_hints
from app.crud.crud_tasks import crud_tasks
from app.crud.crud_tasks_media import crud_tasks_media
from app.crud.crud_users_attempts import crud_users_attempts
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.models.task_media import TaskMedia
from app.schemas.task import TaskRead, TaskAdminRead, TaskCreate, TaskCreateInternal, TaskUpdate, TaskMediaRead
from app.schemas.task_hint import TaskHint, TaskHintRead
from app.schemas.user_task_attempt import TaskAttemptCreateInternal, TaskAttemptRead
from app.schemas.user_task_result import TaskResultRead
from app.settings import settings
from app.utils.encryption import enigma
from app.utils.input import string_washer
from app.utils.user_utils import get_current_user, get_or_create_task_result, get_current_superuser

router = APIRouter()


@router.post("", response_model=TaskAdminRead)
async def post_task(
        request: Request,
        task: TaskCreate,
        user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TaskAdminRead:

    task_internal_dict = task.model_dump()
    if task_internal_dict["answer_regex"] is not None:
        pattern = re.compile(task_internal_dict["answer_regex"], re.IGNORECASE)
        if pattern.search(task_internal_dict["answer_plaintext"]) is None:
            raise HTTPException(status_code=400, detail="Plaintext answer does not match regex")

    task_internal_dict["author"] = user["username"]
    task_internal_dict["created_by_user_id"] = user["id"]

    task_internal = TaskCreateInternal(**task_internal_dict)
    created_task = await crud_tasks.create(db=db, object=task_internal)

    task_read = await crud_tasks.get(db=db, id=created_task.id, schema_to_select=TaskAdminRead)

    if task_read is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return cast(TaskAdminRead, task_read)


@router.patch("/{date}", response_model=TaskAdminRead)
async def patch_task(
        date: datetime.date,
        request: Request,
        values: TaskUpdate,
        current_user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TaskAdminRead:


    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await crud_tasks.update(db=db, object=values, id=db_task["id"])
    db_task = await crud_tasks.get(db=db, id=db_task["id"])

    return cast(TaskAdminRead, db_task)


@router.get("/{date}")
async def get_task_by_date(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
        date: datetime.date = datetime.date.today(),
):
    db_task = await crud_tasks.get(db=db, date=date, schema_to_select=TaskAdminRead)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if user["is_admin"]:
        return TaskAdminRead(**db_task)

    return TaskRead(**db_task)


@router.delete("/{date}")
async def delete_task(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_superuser)],
        date: datetime.date = datetime.date.today(),
):

    if db_task := await crud_tasks.get(db=db, date=date):
        await crud_tasks.delete(db=db, id=db_task["id"])
        return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")


