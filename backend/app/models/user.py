import datetime
from typing import Optional, List, Annotated

from fastapi import HTTPException
from fastapi.params import Depends

from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.orm import Mapped, relationship

from starlette import status

from app.database import Base
from app.models.task_tracker import TaskResult
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, oauth2_scheme, decode_payload, generate_uid


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = Column(autoincrement=True, primary_key=True, init=False)

    username: Mapped[str] = Column(String(30), nullable=False)
    full_name: Mapped[str] = Column(String(50), nullable=False)
    email: Mapped[str] = Column(String(30), unique=True, nullable=False)
    hashed_password: Mapped[str] = Column(String)

    email_verified: Mapped[bool] = Column(Boolean, default=False)
    results: Mapped[List] = relationship(back_populates="user", cascade_delete=True, default=[])

    uuid: Mapped[str] = Column(String, unique=True, nullable=False, default_factory=generate_uid())
    created_at: Mapped[datetime.datetime] = Column(DateTime(timezone=True), default_factory=lambda: datetime.datetime.now(
        datetime.UTC))
    updated_at: Mapped[datetime.datetime | None] = Column(DateTime(timezone=True), default=None)

    @classmethod
    def create_user(cls, user: "UserCreate") -> "User":
        user_dict = user.model_dump()
        hashed_password = get_password_hash(password=user_dict.pop("password"))
        user_dict["hashed_password"] = hashed_password
        return cls(**user_dict)

    @classmethod
    def get_user_by_username_or_email(cls, username: str) -> Optional["User"]:
        with session_scope() as session:
            if user := (
                    session.exec(
                        select(cls)
                                .where(or_(
                            cls.username == username,
                            cls.email == username)))
                            .first()):
                return user
        return None


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
