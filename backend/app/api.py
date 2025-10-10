from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import user, time, task, login, media  # , admin_users, admin_task, media
from app.database import async_engine as engine, Base
from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger


# The task to run
def my_secondly_task():
    print(f"Task is running at {datetime.now()}")
    # ... additional task code goes here ...

# scheduler = BackgroundScheduler()
# trigger = CronTrigger(second=0)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("startup")
    yield
    print("shutdown")
    # scheduler.shutdown()

app = FastAPI(lifespan=app_lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(time.router, prefix="/time", tags=["time"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(task.router, prefix="/task", tags=["task"])
app.include_router(media.router, prefix="/media", tags=["media"])
# app.include_router(admin_users.router, prefix="/admin/user", tags=["Admin Users"])
# app.include_router(admin_task.router, prefix="/admin/task", tags=["Admin Tasks"])