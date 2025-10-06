import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.task_tracker import TaskResult

from app.utils.security import generate_uid

class MediaTypes(str, Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    MP3 = "audio/mp3"
    MP4 = "video/mp4"
    MD = "text/markdown"


class TaskMedia(SQLModel, table=True):
    file_name: str = Field(nullable=False, primary_key=True)
    hint_number: int = Field(default=0, nullable=False)
    date: datetime.date = Field(foreign_key="task.date")
    media_type: MediaTypes
    description: str = Field(nullable=True)
    task: "Task" = Relationship(back_populates="media")

    def is_locked(self, user, session) -> bool:
        match self.task.status:
            case "closed": return True
            case "expired": return False
            case "open":
                if task_tracker := TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session):
                    return self.hint_number > task_tracker.hints_used
            case _:
                return False

        if task_tracker := TaskResult.get_or_create_daily_task_tracker(user_id=user.id, session=session):
            return self.hint_number > task_tracker.hints_used

        return False

    @classmethod
    def create_media_dict(cls, file, date, hint_number):
        file_name = generate_uid() + "." + file.filename.split(".")[-1]
        file_extension = file.filename.split(".")[-1]
        task_media_dict = {
            "date": date,
            "file_name": file_name,
            "media_type": MediaTypes[file_extension.upper()],
            "description": "desc",
            "hint_number": hint_number,
        }
        return cls(**task_media_dict)
