from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.crud.crud_users import crud_users
from app.database import async_get_db
from app.utils.security import oauth2_scheme, decode_payload


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(async_get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token_data := decode_payload(token):
        if "@" in token_data.username:
            user = await crud_users.get(db=db, email=token_data.username, is_deleted=False)
        else:
            user = await crud_users.get(db=db, username=token_data.username, is_deleted=False)

        if user:
            if hasattr(user, 'model_dump'):
                return user.model_dump()
            else:
                return user

    raise credentials_exception
