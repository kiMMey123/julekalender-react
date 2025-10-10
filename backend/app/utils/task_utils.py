import datetime
from typing import cast

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_attempts import crud_users_attempts
from app.schemas.task import TaskRead
from app.schemas.user_task_attempt import TaskAttemptRead
from app.schemas.user_task_result import TaskResultWithAnswer
from app.utils.encryption import enigma
from app.utils.user_utils import get_or_create_task_result


async def get_current_task(db: AsyncSession) -> TaskRead:
    db_task = await crud_tasks.get(db=db, date=datetime.date.today(), is_deleted=False)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return cast(TaskRead, db_task)


async def check_answer(db: AsyncSession, user_id: int, answer: str) -> TaskResultWithAnswer:
    db_task = await crud_tasks.get(db=db, date=datetime.date.today(), is_deleted=False)

    result = await get_or_create_task_result(db=db, user_id=user_id, task_id=db_task["id"])
    result = TaskResultWithAnswer(**result.model_dump(), text=answer, msg="incorrect")

    task_attempts = await crud_users_attempts.get_multi(db=db, user_id=user_id, task_id=db_task["id"],
                                                        schema_to_select=TaskAttemptRead)
    result.attempts = [TaskAttemptRead(**t) for t in task_attempts["data"]]

    if result.solved:
        result.msg = "solved"

    elif result.attempts_left <= 0:
        result.msg = "no_attempts"

    else:
        if answer in [t.text for t in result.attempts]:
            result.msg = "duplicate"

        elif enigma.compare_answer(answer, db_task["answer_regex"] or db_task["answer_plaintext"]):
            result.msg = "correct"

    return result
