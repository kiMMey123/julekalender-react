from datetime import datetime, UTC, date

from sqlalchemy import Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import generate_uid


class TaskAttempt(Base):
    __tablename__ = 'task_attempt'
    answer: Mapped[str] = mapped_column(String, nullable=False)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'), nullable=False)
    task_result_id: Mapped[int] = mapped_column(Integer, ForeignKey('task_result.id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, ForeignKey('task_result.date'), nullable=False)

    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=False, default_factory=generate_uid)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)