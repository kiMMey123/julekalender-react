from datetime import timedelta
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.crud.crud_users import crud_users
from app.database import async_get_db
from app.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, Token, authenticate_user

router = APIRouter()


@router.post("/token")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(async_get_db)],
):
    this_user = await crud_users.get(db=db, username=form_data.username)
    this_user = authenticate_user(this_user, form_data.password)

    if not this_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": this_user["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
