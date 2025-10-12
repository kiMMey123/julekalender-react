import datetime
import os
from typing import Annotated, cast, Union

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response, FileResponse

from app.crud.crud_tasks import crud_tasks
from app.crud.crud_tasks_hints import crud_tasks_hints
from app.crud.crud_tasks_media import crud_tasks_media
from app.database import async_get_db
from app.models.task_media import MediaTypes
from app.schemas.task_media import TaskMediaCreateInternal, TaskMediaRead
from app.settings import settings
from app.utils.security import generate_uid
from app.utils.user_utils import get_current_superuser, get_current_user

router = APIRouter()

@router.post("")
async def upload_file(
        db: Annotated[AsyncSession, Depends(async_get_db)],
        user: Annotated[dict, Depends(get_current_superuser)],
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

    file_extension = file.filename.split(".")[-1]
    file_name = generate_uid() + "." + file_extension
    file_path = os.path.join(settings.FILES_PATH, file_name)

    try:
        with open(file_path, "wb") as f:
            while contents := await file.read(1024 * 1024):
                f.write(contents)

        created_media = await crud_tasks_media.create(
            db=db, object=TaskMediaCreateInternal(date=date, hint_number=hint_number, info="test",
                                                  media_type=MediaTypes[file_extension.upper()], file_name=file_name,
                                                  task_id=task["id"]))
        if not created_media:
            raise HTTPException(status_code=500, detail="Task media creation failed")
        new_media = await crud_tasks_media.get(db=db, id=created_media.id, schema_to_select=TaskMediaRead)

        return cast(TaskMediaRead, new_media)

    except Exception as e:
        raise e


@router.get("/{file_name_or_id}", response_model=TaskMediaRead)
async def get_media(
        file_name_or_id: Union[int, str],
        user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    if file_name_or_id.isdigit():
        media = await crud_tasks_media.get(db=db, id=file_name_or_id, is_deleted=False, schema_to_select=TaskMediaRead)
    else:
        media = await crud_tasks_media.get(db=db, file_name=file_name_or_id, is_deleted=False,
                                           schema_to_select=TaskMediaRead)

    if not media:
        raise HTTPException(status_code=404, detail=f'media <{file_name_or_id}> not found')

    return cast(TaskMediaRead, media)




@router.delete("/{file_name_or_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        user: Annotated[dict, Depends(get_current_superuser)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
        file_name_or_id: Union[int, str],

):
    if file_name_or_id.isdigit():
        media = await crud_tasks_media.get(db=db, id=file_name_or_id, is_deleted=False)
    else:
        media = await crud_tasks_media.get(db=db, file_name=file_name_or_id, is_deleted=False)

    if not media:
        raise HTTPException(status_code=404, detail=f'media <{file_name_or_id}> not found')

    else:
        try:
            file_path = os.path.join(settings.FILES_PATH, media["file_name"])
            if os.path.isfile(file_path):
                os.remove(file_path)

            await crud_tasks_media.delete(db=db, id=media["id"])
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

#
@router.get("/download/{file_name_or_id}")
async def download_file(
        file_name_or_id: Union[int, str],
        user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    if file_name_or_id.isdigit():
        media = await crud_tasks_media.get(db=db, id=file_name_or_id, is_deleted=False, schema_to_select=TaskMediaRead)
    else:
        media = await crud_tasks_media.get(db=db, file_name=file_name_or_id, is_deleted=False,
                                           schema_to_select=TaskMediaRead)

    if not media:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_path = os.path.join(settings.FILES_PATH, media["file_name"])
    
    if not os.path.exists(file_path):
        return HTTPException(status_code=404, detail="File not found")
    else:
        return FileResponse(str(file_path), media_type=media["media_type"])
