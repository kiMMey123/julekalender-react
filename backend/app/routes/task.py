from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import SessionDep, session_scope
from app.schemas.task import UserAnswer, Task, TaskHint, UserTaskAttempt
from app.schemas.user import User, UserCreate, UserTask, UserRead, get_user_tasks, get_current_user

from typing import Annotated, Optional
from fastapi.params import Depends

from app.utils.encryption import enigma

router = APIRouter()

async def get_current_task():
    task = Task.get_active_task()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/answer", response_model=UserTask)
async def answer_task(
    user: Annotated[User, Depends(get_current_user)],
    answer: UserAnswer
):
    try:
        with session_scope() as session:
            task = Task.get_active_task(session)
            exception_dict = {"message": ""}
            user_task = UserTask.get_or_create_daily_task(user_id=user.id, session=session)
            answer_txt = answer.text.strip().lower()
            attempt_result = user_task.add_attempt(text=answer_txt, session=session)


            if attempt_result == "ok":
                is_correct_answer = task.check_answer(text=answer_txt, session=session)
                print(is_correct_answer)
                if is_correct_answer:
                    user_task.set_solved(session=session)
                    session.add(user_task)

                    session.commit()
            else:
                if attempt_result == "duplicate":
                    raise HTTPException(status_code=400, detail={
                        "type": "duplicate",
                        "message": "input is a duplicate from previous attempt",
                        "input": answer.text
                    })
                if attempt_result == "no_attempts":
                    raise HTTPException(status_code=429, detail={"type": "attempt", "time": user_task.attempts_reset.isoformat()})

            return user_task
    except IntegrityError:
        raise HTTPException(status_code=404, detail="User not found")




@router.get("/hint", response_model=list[Optional[TaskHint]])
async def get_user_hint(
        session: SessionDep,
        user: Annotated[User, Depends(get_current_user)],
        task: Annotated[Task, Depends(get_current_task)],
):
    return []