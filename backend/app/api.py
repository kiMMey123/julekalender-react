from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.routes import user, time, admin_users, task, admin_task, media
from app.models.user import User
from app.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, Token
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

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    this_user = User.get_user_by_username_or_email(form_data.username)

    if not this_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": this_user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

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

app.include_router(time.router, prefix="/time", tags=["time"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(task.router, prefix="/task", tags=["task"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(admin_users.router, prefix="/admin/user", tags=["Admin Users"])
app.include_router(admin_task.router, prefix="/admin/task", tags=["Admin Tasks"])