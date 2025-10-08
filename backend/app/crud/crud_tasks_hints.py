from fastcrud import FastCRUD

from app.models.task_hint import TaskHint
from app.schemas.task_hint import TaskHintCreate, TaskHintRead, TaskHintUpdate, TaskHintDelete, TaskHintUpdateInternal

CRUDTaskHint = FastCRUD[TaskHint, TaskHintCreate, TaskHintUpdate, TaskHintUpdateInternal, TaskHintDelete, TaskHintRead]
crud_TaskHints = CRUDTaskHint(TaskHint)