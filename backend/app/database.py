from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from collections.abc import AsyncGenerator

db_file_name = "julekalender.db"
db_url = "sqlite:///" + db_file_name

connect_args = {"check_same_thread": False}
engine = create_engine(db_url, connect_args=connect_args)

class Base(DeclarativeBase, MappedAsDataclass):
    pass

async_engine = create_async_engine(db_url, echo=False, future=True)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db