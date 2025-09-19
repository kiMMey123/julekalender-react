import datetime

import fastapi.staticfiles
from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, and_
from starlette.responses import FileResponse

from app.database import SessionDep, session_scope
from app.schemas.task import  Task, TaskHint
from app.schemas.user import User, TaskTracker, UserAnswerAttempt, UserAnswerReply, get_current_user

from typing import Annotated, Optional
from fastapi.params import Depends

import os

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile):
    files_dir = "..\\files"
    os.makedirs(files_dir, exist_ok=True)
    filename = file.filename
    file_path = os.path.join(files_dir, filename)
    with open(file_path, "wb") as f:
        while contents := await file.read(1024 * 1024):
            f.write(contents)


    return {"filename": file.filename, "file_size": file.size, "location": file_path}

@router.get("/download/{filename}")
async def download_file(
        filename: str,
        user: Annotated[User, Depends(get_current_user)]
):
    files_dir = "..\\files"
    file_path = os.path.join(files_dir, filename)
    if not os.path.exists(file_path):
        return HTTPException(status_code=404, detail="File not found")
    else:
        media_types = {
            "jpg": "image/jpeg",
            "png": "image/png",
            "mp3": "audio/mpeg",
            "md": "text/markdown",
        }
        media_type = media_types.get(filename.split(".")[-1], "application/octet-stream")
        return FileResponse(file_path, media_type=media_type)