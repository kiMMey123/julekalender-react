from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import SessionDep
from app.schemas.task import UserAnswerReply, UserAnswer, Task
from app.schemas.user import User, UserCreate, UserTask, UserRead, get_user_tasks, get_current_user

from typing import Annotated
from fastapi.params import Depends

router = APIRouter()

@router.post("/answer", response_model=UserAnswerReply)
def answer_task(
    session:SessionDep,
    user: Annotated[User, Depends(get_current_user)],
    answer: UserAnswer
):
    try:
        task = Task.get_active_task(session=session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
    except IntegrityError:
        raise HTTPException(status_code=404, detail="User not found")