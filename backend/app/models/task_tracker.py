import datetime
from typing import Optional, List

from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base  # Assuming you have a base declarative class
from app.models.user import User
from app.settings import ATTEMPTS_PER_RESET, SCORES_PER_HINT_USED
from app.utils.input import string_washer


class TaskResult(Base):
    __tablename__ = 'task_tracker'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True, default=datetime.date.today(), unique=True)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    time_solved: Optional[Mapped[datetime.datetime]] = mapped_column(DateTime, nullable=True, default=None)
    score: Mapped[int] = mapped_column(Integer, default=0)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    attempts_left: Mapped[int] = mapped_column(Integer, default=ATTEMPTS_PER_RESET)
    attempts_reset: Optional[Mapped[datetime.datetime]] = mapped_column(DateTime, nullable=True, default=None)
    attempts: Mapped[list] = mapped_column(JSON, default=[])

    __table_args__ = (
        UniqueConstraint("date", "user_id"),
    )

    @classmethod
    def get_or_create_daily_task_tracker(cls, user_id: str, session: Session,
                                         task_date: datetime.date = datetime.date.today()):
        task = session.exec(select(cls).filter_by(user_id=user_id, date=task_date)).first()
        if not task:
            task = cls(user_id=user_id, date=task_date)
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    def check_attempt(self, text: str, task: Task, session) -> str:
        text = string_washer(text)
        message = "incorrect"

        if self.solved:
            message = "solved"
        elif text in self.attempts:
            message = "duplicate"
        elif self.attempts_left <= 0:
            if self.attempts_reset is not None:
                if datetime.datetime.now() >= self.attempts_reset:
                    self.attempts_left = ATTEMPTS_PER_RESET
                    self.attempts_reset = None
                    message = self.check_attempt(text, task, session)
                else:
                    message = "no_attempts"

        else:
            self.attempts.append(text)
            self.attempts_left -= 1

            if self.attempts_left <= 0:
                self.attempts_reset = datetime.datetime.now() + datetime.timedelta(seconds=30)

            attributes.flag_modified(self, 'attempts')

            if task.check_answer(text=text):
                self.solved = True
                self.time_solved = datetime.datetime.now()
                self.score = SCORES_PER_HINT_USED[self.hints_used]
                message = "correct"

        if message not in ["solved", "duplicate", "no_attempts"]:
            session.add(self)
            session.commit()
            session.refresh(self)

        return message
