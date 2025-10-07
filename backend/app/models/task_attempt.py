import datetime

from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskAttempt(Base):
    __tablename__ = 'task_attempt'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    date: Mapped[datetime.date] = mapped_column(Date, ForeignKey('task_result.date'), nullable=False)
    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=False)