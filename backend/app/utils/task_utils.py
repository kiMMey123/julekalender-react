import datetime
from typing import cast

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.annotation import Annotated

from app.crud.crud_tasks import crud_tasks
from app.database import async_get_db
from app.schemas.task import TaskRead
from app.utils.encryption import enigma


async def get_current_task(db: AsyncSession) -> TaskRead:
    db_task = await crud_tasks.get(db=db, date=datetime.date.today(), is_deleted=False)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return cast(TaskRead, db_task)

async def check_task_answer(db: AsyncSession, task_id: int, answer) -> bool:
    task = crud_tasks.get(db=db, id=task_id, is_deleted=False)
    if task["answer_regex"]:
        return enigma.compare_answer(answer, task["answer_regex"])

    return enigma.compare_answer(answer, task["answer_plaintext"])