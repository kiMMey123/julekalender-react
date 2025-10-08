import datetime

from sqlalchemy import Date, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import generate_uid


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    date: Mapped[datetime.date] = mapped_column(Date, unique=True)

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

# def create_or_update_task(data: Union[TaskCreate, TaskUpdate], date) -> TaskAdminRead:
#     try:
#         with session_scope() as session:
#             task_dict = {k: v for k, v in data.model_dump().items() if v is not None}
#
#             for k, v in task_dict.items():
#                 match k:
#                     case "open_time" | "close_time":
#                         task_dict[k] = get_open_close_time(date, v)
#                     case "answer":
#                         task_dict[k] = enigma.encrypt_answer(task_dict.get("answer"))
#                     case "yt_url":
#                         task_dict[k] = task_dict.get("yt_url").unicode_string()
#
#             answer_dict = {
#                 "text": task_dict.pop("answer", None),
#                 "yt_url": task_dict.pop("yt_url", None)
#             }
#
#             if task := Task.get_task(session, date):
#                 if task.status != "closed":
#                     raise HTTPException(status_code=403, detail="cannot edit open or expired task")
#                 for k, v in task_dict.items():
#                     setattr(task, k, v)
#                 answer = task.answer
#                 for k, v in answer_dict.items():
#                     if v is not None:
#                         setattr(answer, k, v)
#
#             else:
#                 task = Task(date=date, **task_dict)
#                 answer = TaskAnswer(date=date, **answer_dict)
#
#             session.add(task)
#             session.add(answer)
#             session.commit()
#             session.refresh(answer)
#             session.refresh(task)
#             return task.get_admin_task()
#
#     except IntegrityError as e:
#         raise HTTPException(status_code=422, detail=str(e))
