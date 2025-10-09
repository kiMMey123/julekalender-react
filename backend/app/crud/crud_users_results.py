from fastcrud import FastCRUD

from app.models.user_task_result import TaskResult
from app.schemas.user_task_result import TaskResultCreate, TaskResultRead, TaskResultUpdate, TaskResultDelete, TaskResultUpdateInternal

CRUDTaskResult = FastCRUD[TaskResult, TaskResultCreate, TaskResultUpdate, TaskResultUpdateInternal, TaskResultDelete, TaskResultRead]
crud_users_results = CRUDTaskResult(TaskResult)