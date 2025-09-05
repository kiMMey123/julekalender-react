from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("")
async def time():
    return {"time": datetime.isoformat(datetime.now())}

