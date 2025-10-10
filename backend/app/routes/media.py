import datetime
import os
from typing import Annotated, cast

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.responses import FileResponse

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_tasks_hints import crud_tasks_hints
from app.crud.crud_tasks_media import crud_tasks_media
from app.database import async_get_db
from app.models.task_media import TaskMedia, MediaTypes
from app.schemas.task_media import TaskMediaCreateInternal, TaskMediaCreate, TaskMediaRead
from app.utils.security import generate_uid

router = APIRouter()


@router.post("")
async def upload_file(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        file: UploadFile,
        date: datetime.date,
        hint_number: int

):
    if hint_number > 5 or hint_number < 0:
        raise HTTPException(status_code=403, detail="Not allowed")

    if await crud_tasks_media.exists(db=db, date=date, is_deleted=False, hint_number=hint_number):
        raise HTTPException(status_code=400, detail="Media already exists")

    if not await crud_tasks.exists(db=db, date=date, is_deleted=False):
        raise HTTPException(status_code=404, detail="Task not found")
    else:
        task = await crud_tasks.get(db=db, date=date, is_deleted=False)

    if not await crud_tasks_hints.exists(db=db, date=date, hint_number=hint_number,
                                         is_deleted=False) and hint_number > 0:
        raise HTTPException(status_code=404, detail="Hint not found")

    files_dir = "..\\files"
    os.makedirs(files_dir, exist_ok=True)
    file_extension = file.filename.split(".")[-1]
    file_name = generate_uid() + "." + file_extension
    file_path = os.path.join(files_dir, file_name)

    try:
        with open(file_path, "wb") as f:
            while contents := await file.read(1024 * 1024):
                f.write(contents)

        created_media = await crud_tasks_media.create(
            TaskMediaCreateInternal(date=date, hint_number=hint_number, info="test", media_type=MediaTypes[file_extension], file_name=file_name,
                                    task_id=task["id"]))
        if not created_media:
            raise HTTPException(status_code=500, detail="Task media creation failed")
        new_media = crud_tasks_media.get(db=db, id=created_media.id, schema_to_select=TaskMediaRead)

        return cast(TaskMediaRead, new_media)

    except Exception as e:
        raise e



@router.delete("/{file_name}")
async def delete_file(
        file_name: str,

):
    pass

#
# @router.get("/download/{file_name}")
# async def download_file(
#         file_name: str,
#         # user: Annotated[User, Depends(get_current_user)],
# ):
#     with session_scope() as session:
#         media = session.exec(select(TaskMedia).where(Taskfile_name == file_name)).first()
#
#         if not media:
#             raise HTTPException(status_code=404, detail="File not found")
#
#         # if is_locked(user, session):
#         #     raise HTTPException(status_code=403, detail="File not accessible")
#
#     files_dir = "..\\files"
#     file_path = os.path.join(files_dir, file_name)
#     if not os.path.exists(file_path):
#         return HTTPException(status_code=404, detail="File not found")
#     else:
#         return FileResponse(file_path, media_type=media_type)
