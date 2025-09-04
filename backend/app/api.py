from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager

from app.database import create_db_and_tables, SessionDep
from app.routes import user, time, admin
from app.schemas.user import User
from app.utils.security import fake_hash_password


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    create_db_and_tables()
    print("startup")
    yield
    print("shutdown")

app = FastAPI(lifespan=app_lifespan)

@app.post("/token")
async def login(session:SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    this_user = User.get_user_by_username_or_email(session, form_data.username)
    if not this_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == this_user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {"access_token": this_user.username, "token_type": "bearer"}

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
app.include_router(admin.router, prefix="/admin", tags=["admin"])