import datetime

import pydantic
from pydantic import BaseModel, Field,HttpUrl
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import TaskHint, TaskAnswer
    from app.models.media import TaskMedia

class TaskBase(BaseModel):
    info: str
    author: Optional[str] = None


class TaskCreate(BaseModel):
    info: str
    author: Optional[str]
    answer: str
    open_time: int = Field(default=9, ge=6, le=22)
    close_time: int = Field(default=23, gt=19, le=23)
    yt_url: Optional[HttpUrl]

class TaskUpdate(BaseModel):
    info: Optional[str]
    author: Optional[str]
    answer: Optional[str]
    open_time: Optional[int] = Field(default=9, ge=6, le=22)
    close_time: Optional[int] = Field(default=23, gt=19, le=23)
    yt_url: Optional[HttpUrl]

class TaskUserRead(BaseModel):
    date: datetime.date
    open_time: datetime.datetime
    close_time: datetime.datetime
    info: str
    status: str

class TaskAdminRead(TaskUserRead):
    answer_plaintext: str
    answer: 'TaskAnswer'
    hints: Optional[List['TaskHint']] = None
    media: Optional[List['TaskMedia']] = None


class TaskHintCreate(BaseModel):
    info: Optional[str]


