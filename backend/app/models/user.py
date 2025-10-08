from datetime import datetime, UTC

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import generate_uid


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)

    username: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String)
    name_show: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_show: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=False, default_factory=generate_uid)
    is_admin: bool = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
