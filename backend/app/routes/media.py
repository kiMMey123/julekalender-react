import datetime
import os
from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import Depends
from sqlmodel import select
from starlette.responses import FileResponse

from app.database import session_scope
from app.schemas.task import Task, TaskMedia
from app.schemas.user import User, get_current_user

router = APIRouter()


@router.post("/upload/")
async def upload_file(file: UploadFile, date: datetime.date, hint_number: int = 0):
    files_dir = "..\\files"
    os.makedirs(files_dir, exist_ok=True)
    task_media = TaskMedia.create_media_dict(file, date, hint_number)
    file_path = os.path.join(files_dir, task_media.file_name)

    with session_scope() as session:
        if Task.get_task(session, date) is None:
            raise HTTPException(400, detail=f'Task on date {date} does not exist')
        with open(file_path, "wb") as f:
            while contents := await file.read(1024 * 1024):
                f.write(contents)
        session.add(task_media)
        session.commit()
        session.refresh(task_media)

        return task_media


@router.get("/download/{file_name}")
async def download_file(
        file_name: str,
        user: Annotated[User, Depends(get_current_user)],
):
    with session_scope() as session:
        media = session.exec(select(TaskMedia).where(TaskMedia.file_name == file_name)).first()

        if not media:
            raise HTTPException(status_code=404, detail="File not found")

        if media.is_locked(user, session):
            raise HTTPException(status_code=403, detail="File not accessible")

    files_dir = "..\\files"
    file_path = os.path.join(files_dir, file_name)
    if not os.path.exists(file_path):
        return HTTPException(status_code=404, detail="File not found")
    else:

        return FileResponse(file_path, media_type=media.media_type)
