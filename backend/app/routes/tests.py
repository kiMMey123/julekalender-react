from fastapi import APIRouter
from datetime import datetime

from pydantic import BaseModel

from app.settings import JULEKALENDER_ANSWER_KEY
from app.utils.encryption import Enigma
from app.database import SessionDep
from app.schemas.user import User, UserCreate, TaskTracker, UserRead, get_user_task_trackers, get_current_user

from typing import Annotated
from fastapi.params import Depends

enigma = Enigma(JULEKALENDER_ANSWER_KEY)

router = APIRouter()

class AnswerCreate(BaseModel):
    input: str
    orig: str

@router.post("/encryption")
async def test_encryption(data: AnswerCreate):
    orig = enigma.encrypt_answer(data.orig)
    answer = data.input
    is_same = enigma.compare_answer(answer, orig)
    return {"orig": orig, "answer": answer, "is_same": is_same}

@router.post("/answer")
async def test_answer(session:SessionDep,
    user: Annotated[User, Depends(get_current_user)], answer: str):
    return {"ans": answer, "user": user.id}
