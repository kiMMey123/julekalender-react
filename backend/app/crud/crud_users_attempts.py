from fastcrud import FastCRUD

from app.models.user_task_attempt import TaskAttempt
from app.schemas.user_task_attempt import TaskAttemptCreate, TaskAttemptRead, TaskAttemptUpdate, TaskAttemptDelete, \
    TaskAttemptUpdateInternal

CRUDTaskAttempt = FastCRUD[
    TaskAttempt, TaskAttemptCreate, TaskAttemptUpdate, TaskAttemptUpdateInternal, TaskAttemptDelete, TaskAttemptRead]
crud_users_attempts = CRUDTaskAttempt(TaskAttempt)
