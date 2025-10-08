from fastcrud import FastCRUD

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate, TaskDelete, TaskUpdateInternal

CRUDTask = FastCRUD[Task, TaskCreate, TaskUpdate, TaskUpdateInternal, TaskDelete, TaskRead]
crud_tasks = CRUDTask(Task)