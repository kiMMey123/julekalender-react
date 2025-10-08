from datetime import datetime, UTC
from typing import Optional, List, Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, relationship, mapped_column
from starlette import status

from app.database import Base
from app.models.user_task_result import TaskResult
from app.utils.security import get_password_hash, oauth2_scheme, decode_payload, generate_uid


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)

    username: Mapped[str] = mapped_column(String(30), nullable=False)
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String)
    full_name_show: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_show: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=False, default_factory=generate_uid)
    is_admin: bool = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)


def get_user_task_trackers(session, user):
    trackers = session.query(TaskResult).filter_by(user_id=user).all()
    return trackers


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_data := decode_payload(token):
        user = User.get_user_by_username_or_email(token_data.username)
        if not user:
            raise credentials_exception
        return user
    raise credentials_exception
