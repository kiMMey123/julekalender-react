import datetime
from typing import cast

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_users_attempts import crud_users_attempts
from app.schemas.task import TaskRead
from app.schemas.user_task_attempt import TaskAttemptRead
from app.utils.encryption import enigma
from app.utils.user_utils import get_or_create_task_result


async def get_current_task(db: AsyncSession) -> TaskRead:
    db_task = await crud_tasks.get(db=db, date=datetime.date.today(), is_deleted=False)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return cast(TaskRead, db_task)


async def check_answer(db: AsyncSession, user_id: int, answer: str) -> str:
    db_task = await crud_tasks.get(db=db, date=datetime.date.today(), is_deleted=False)

    result = await get_or_create_task_result(db=db, user_id=user_id, task=db_task)
    if result["solved"]:
        return "solved"

    elif result["attempts_left"] <= 0:
        return "no_attempts"

    else:
        task_attempts = await crud_users_attempts.get_multi(db=db, user_id=user_id, task_id=db_task["id"],
                                                            schema_to_select=TaskAttemptRead)

        result.attempts = [TaskAttemptRead(**t) for t in task_attempts["data"]]

        if answer in [t.text for t in task_attempts["data"]]:
            return "duplicate"

        elif enigma.compare_answer(answer, db_task["answer_regex"] or db_task["answer_plaintext"]):
            return "correct"

        else:
            return "incorrect"
