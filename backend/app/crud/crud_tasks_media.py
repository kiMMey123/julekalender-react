from fastcrud import FastCRUD

from app.models.task_media import TaskMedia
from app.schemas.task_media import TaskMediaCreate, TaskMediaRead, TaskMediaUpdate, TaskMediaDelete, TaskMediaUpdateInternal

CRUDTaskMedia = FastCRUD[TaskMedia, TaskMediaCreate, TaskMediaUpdate, TaskMediaUpdateInternal, TaskMediaDelete, TaskMediaRead]
crud_tasks_media = CRUDTaskMedia(TaskMedia)