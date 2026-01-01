from datetime import datetime, date, UTC

from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.settings import settings
from app.utils.security import generate_uid


class TaskResult(Base):
    __tablename__ = 'user_task_result'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'))

    date: Mapped[date] = mapped_column(Date, default=date.today(), unique=True, index=True)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    time_solved: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    score: Mapped[int] = mapped_column(Integer, default=0)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    attempts_left: Mapped[int] = mapped_column(Integer, default=settings.ATTEMPTS_PER_RESET)
    attempts_reset: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)

    uuid: Mapped[str] = mapped_column(String, unique=True, default_factory=lambda: generate_uid())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)

    __table_args__ = (
        UniqueConstraint("date", "user_id"),
    )

