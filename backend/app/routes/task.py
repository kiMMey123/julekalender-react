import datetime
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
from app.schemas.user_task_result import TaskResultWithAnswer
from app.settings import settings
from app.utils.input import string_washer
from app.utils.task_utils import check_answer
from app.utils.user_utils import get_current_user, get_or_create_task_result

router = APIRouter()


@router.post("", response_model=TaskAdminRead)
async def post_task(
        request: Request,
        task: TaskCreate,
        user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TaskAdminRead:
    if not user["is_admin"]:
        raise HTTPException(status_code=403)

    task_internal_dict = task.model_dump()
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
        user: Annotated[dict, Depends(get_current_user)],
        date: datetime.date = datetime.date.today(),
):
    if not user["is_admin"]:
        raise HTTPException(status_code=403)
    if db_task := await crud_tasks.get(db=db, date=date):
        await crud_tasks.delete(db=db, id=db_task["id"])
        return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/answer", response_model=TaskResultWithAnswer)
async def answer_task(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
        answer: str
):
    db_task = await crud_tasks.get(db=db, date=datetime.date.today())

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if TaskRead(**db_task).status != 'open':
        raise HTTPException(status_code=400, detail='Task is not open')

    washed_answer = string_washer(answer)

    result = await check_answer(db=db, user_id=user["id"], answer=washed_answer)

    if result.solved:
        return result

    if result.msg == "no_attempts":
        if datetime.datetime.now() >= result.attempts_reset:
            updated_result = {"attempts_reset": None, "attempts_left": settings.ATTEMPTS_PER_RESET}

            await crud_users_results.update(db=db, id=result.id, object=updated_result)
            result = await check_answer(db=db, user_id=user["id"], answer=washed_answer)
        else:
            raise HTTPException(status_code=429)

    if result.msg == "duplicate":
        raise HTTPException(status_code=400, detail="duplicate")

    new_result = {"attempts_left": result.attempts_left - 1}

    task_answer = TaskAttemptCreateInternal(date=datetime.date.today(), msg=result.msg, text=result.text,
                                            user_id=user["id"], task_result_id=result.id, task_id=db_task["id"])

    new_attempt = await crud_users_attempts.create(db=db, object=task_answer)
    result.attempts.append(await crud_users_attempts.get(db=db, id=new_attempt.id, schema_to_select=TaskAttemptRead))

    if result.msg == "correct":
        new_result["solved"] = True
        new_result["time_solved"] = datetime.datetime.now()
        new_result["score"] = settings.SCORES_PER_HINT_USED[result.hints_used]
        new_result["attempts_left"] = 0
        new_result["attempts_reset"] = None

    elif new_result["attempts_left"] <= 0:
        new_result["attempts_reset"] = datetime.datetime.now() + datetime.timedelta(minutes=1)

    await crud_users_results.update(db=db, id=result.id, object=new_result)
    updated_result = await crud_users_results.get(db=db, id=result.id)
    result = TaskResultWithAnswer(**updated_result, msg=result.msg, text=result.text, attempts=result.attempts)

    return result

@router.get("{date}/hint", response_model=list[Optional[TaskHintRead]])
async def get_user_hint(
        date: datetime.date,
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
):
        db_task = await crud_tasks.get(db=db, date=date)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        user_result = await get_or_create_task_result(db=db, user_id=user["id"], task_id=db_task["id"])
        if user_result.hints_used == 0 and TaskRead(**db_task).status != 'expired':
            return []
        else:
            hints = crud_tasks_hints.get_multi(db=db, task_id=db_task["id"], schema_to_select=TaskHintRead)
            media = crud_tasks_media.get_multi(db=db, task_id=db_task["id"], schema_to_select=TaskMediaRead)
            user_hints = [h for h in hints["data"] if h["hint_number"] <= user_result.hints_used]

            for hint in user_hints:
                hint["media"] = [TaskMediaRead(**m) for m in media["data"] if m["hint_number"] == hint["hint_number"]]
            return [TaskHintRead(**h) for h in user_hints]


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
