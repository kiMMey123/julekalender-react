import datetime
from typing import Annotated, cast, Optional, Union

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_results import crud_task_results
from app.database import async_get_db
from app.schemas.task import TaskRead, TaskAdminRead, TaskCreate, TaskCreateInternal, Task, TaskUpdate
from app.schemas.user_task_result import TaskResultRead, TaskResultCreateInternal
from app.utils.task_utils import get_current_task
from app.utils.user_utils import get_current_user

router = APIRouter()

@router.post("", response_model=TaskAdminRead)
async def post_task(
        request: Request,
        task: TaskCreate,
        current_user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TaskAdminRead:

    if not current_user["is_admin"]:
        raise HTTPException(status_code=403)

    task_internal_dict = task.model_dump()
    task_internal_dict["author"] = current_user["username"]
    task_internal_dict["created_by_user_id"] = current_user["id"]

    task_internal = TaskCreateInternal(**task_internal_dict)
    created_task = await crud_tasks.create(db=db, object=task_internal)

    task_read = await crud_tasks.get(db=db, id=created_task.id, schema_to_select=Task)

    if task_read is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return cast(TaskAdminRead, task_read)

@router.patch("/{date}", response_model=TaskAdminRead)
async def patch_task(
        date: datetime.date,
        request: Request,
        values: TaskUpdate,
        current_user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TaskAdminRead:

    if not current_user["is_admin"]:
        raise HTTPException(status_code=403)

    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await crud_tasks.update(db=db, object=values, id=db_task["id"])
    db_task = await crud_tasks.get(db=db, id=db_task["id"])

    db_task["media"] = []
    db_task["hints"] = []

    return cast(TaskAdminRead, db_task)

@router.get("/{date}")
async def get_task_by_date(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
        date: datetime.date = datetime.date.today(),
):
    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)
    print(db_task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task["media"] = []
    db_task["hints"] = []

    if user["is_admin"]:
        return TaskAdminRead(**db_task)

    return TaskRead(**db_task)

@router.post("/answer")
async def answer_task(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    answer: str
):
    task = await get_current_task(db=db)

    if task["status"] != "open":
        raise HTTPException(status_code=400)




# @router.get("/hint", response_model=list[Optional[TaskHint]])
# async def get_user_hint(
#         user: Annotated[User, Depends(get_current_user)],
#         task: Annotated[Task, Depends(get_current_task)]
# ):
#     with session_scope() as session:
#         task_tracker = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
#         if task_tracker.solved:
#             return task.hints
#
#         hints = session.exec(
#             select(TaskHint)
#             .where(and_(
#                 TaskHint.date == task_tracker.date,
#                 TaskHint.hint_number <= task_tracker.hints_used
#             ))
#         ).all()
#
#         return hints
#
#
# @router.post("/hint/unlock", status_code=204)
# async def unlock_user_hint(
#         user: Annotated[User, Depends(get_current_user)],
#         task: Annotated[Task, Depends(get_current_task)],
# ):
#     with session_scope() as session:
#         task_tracker = TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session)
#         if task_tracker.solved:
#             raise HTTPException(status_code=400, detail="Task is already solved")
#         if task_tracker.hints_used >= len(task.hints):
#             raise HTTPException(status_code=400, detail={"type": "hint", "message": "no hints left"})
#         else:
#             task_tracker.hints_used += 1
#             session.add(task_tracker)
#             session.commit()
