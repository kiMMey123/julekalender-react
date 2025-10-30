import datetime
from typing import Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_users_results import crud_users_results
from app.database import async_get_db
from app.schemas.user_task_result import TaskResultRead


# The task to run
async def update_result_metadata(
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    results = await crud_users_results.get_multi(db=db, date=datetime.date.today(), solved=True, is_deleted=False,
                                           schema_to_select=TaskResultRead, limit=None)


scheduler = BackgroundScheduler()
trigger = CronTrigger(second=0)

scheduler.add_job(func=update_result_metadata, trigger=trigger)
