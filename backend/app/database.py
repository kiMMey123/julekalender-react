from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.declarative import declarative_base

from collections.abc import AsyncGenerator

db_file_name = "julekalender.db"
db_url = "sqlite+aiosqlite:///" + db_file_name

connect_args = {"check_same_thread": False}

async_engine = create_async_engine(db_url, echo=False, future=True)

class Base(DeclarativeBase, MappedAsDataclass):
    pass


local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db