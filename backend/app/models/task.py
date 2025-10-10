import datetime

from sqlalchemy import Date, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import generate_uid


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    date: Mapped[datetime.date] = mapped_column(Date, unique=False, index=True)

    info: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    answer_plaintext: Mapped[str] = mapped_column(String, nullable=False)
    answer_regex: Mapped[str] = mapped_column(String, nullable=True)
    answer_info: Mapped[str] = mapped_column(String, nullable=False)
    yt_url: Mapped[str] = mapped_column(String, nullable=False)

    open_at: Mapped[int] = mapped_column(Integer, nullable=False, default=9)
    close_at: Mapped[int] = mapped_column(Integer, nullable=False, default=23)

    uuid: Mapped[str]= mapped_column(String, unique=True, nullable=False, default_factory=generate_uid)
    created_at: Mapped[datetime.datetime]= mapped_column(DateTime(timezone=True),
                                                   default_factory=lambda: datetime.datetime.now(
                                                       datetime.UTC))
    updated_at: Mapped[datetime.datetime | None]= mapped_column(DateTime(timezone=True), default=None)

    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)