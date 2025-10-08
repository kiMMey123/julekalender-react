from datetime import date, datetime, UTC

from sqlalchemy import UniqueConstraint, Date, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import generate_uid


class TaskHint(Base):
    __tablename__ = 'task_hint'

    __table_args__ = (
        UniqueConstraint("date", "hint_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, ForeignKey('task.date'), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'), nullable=False)
    hint_number: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)

    uuid: Mapped[str] = mapped_column(String, unique=True, default_factory=lambda: generate_uid())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
