import datetime
from typing import Annotated, Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_attempts import crud_users_attempts
from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.schemas.task import TaskRead
from app.schemas.user_task_attempt import TaskAttemptCreateInternal, TaskAttemptRead
from app.settings import settings
from app.utils.encryption import enigma
from app.utils.input import string_washer
from app.utils.user_utils import get_current_user, get_or_create_task_result

router = APIRouter()


@router.get("/{date}", response_model=Optional[List[TaskAttemptRead]])
async def get_task_attempts(
        user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    db_task = await crud_tasks.get(db=db, date=datetime.date.today())
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_attempts = await crud_users_attempts.get_multi(db=db, user_id=user["id"], task_id=db_task["id"],
                                                        schema_to_select=TaskAttemptRead)
    return task_attempts["data"]


@router.post("/{date}", response_model=TaskAttemptRead)
async def answer_task(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_user)],
        a: str,
        date: datetime.date
):
    db_task = await crud_tasks.get(db=db, date=date, is_deleted=False)

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if TaskRead(**db_task).status != 'open':
        raise HTTPException(status_code=400, detail='Task is not open')

    user_result = await get_or_create_task_result(db=db, user_id=user["id"], task=db_task)
    washed_answer = string_washer(a)

    if user_result.solved:
        return TaskAttemptRead(msg="solved", text=a, created_at=datetime.datetime.now())

    if user_result.attempts_left == 0:
        if datetime.datetime.now() >= user_result.attempts_reset:
            updated_result = {"attempts_reset": None, "attempts_left": settings.ATTEMPTS_PER_RESET}

            await crud_users_results.update(db=db, id=user_result.id, object=updated_result)
            user_result = await crud_users_results.get(db=db, id=user_result.id)
        else:
            return TaskAttemptRead(msg="no_attempts", text=a)

    task_attempts = await crud_users_attempts.get_multi(db=db, user_id=user["id"], task_id=db_task["id"],
                                                        schema_to_select=TaskAttemptRead)

    if washed_answer in [t["text"] for t in task_attempts["data"]]:
        return TaskAttemptRead(msg="duplicate", text=a)

    new_result = {"attempts_left": user_result.attempts_left - 1}

    task_attempt = TaskAttemptCreateInternal(date=datetime.date.today(), msg="incorrect", text=washed_answer,
                                             user_id=user["id"], task_result_id=user_result.id,
                                             task_id=db_task["id"]
                                             )

    if enigma.compare_answer(washed_answer, db_task["answer_regex"] or db_task["answer_plaintext"]):
        task_attempt.msg = "correct"

        new_result["solved"] = True
        new_result["time_solved"] = datetime.datetime.now()
        new_result["score"] = settings.SCORES_PER_HINT_USED[user_result.hints_used]
        new_result["attempts_left"] = 0
        new_result["attempts_reset"] = None

    elif new_result["attempts_left"] <= 0:
        new_result["attempts_reset"] = datetime.datetime.now() + datetime.timedelta(minutes=1)

    await crud_users_attempts.create(db=db, object=task_attempt)

    await crud_users_results.update(db=db, id=user_result.id, object=new_result)

    return task_attempt
