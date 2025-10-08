import datetime
from typing import Optional, Annotated
from app.schemas.core import TimestampSchema, PersistentDeletion
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=30, examples=["Kari Nordmann"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["brukersen"])]
    email: Annotated[EmailStr, Field(examples=["kari.nordmann@example.com"])]

class User(TimestampSchema, PersistentDeletion, UserBase):
    email: Annotated[EmailStr, Field(examples=["kari.nordmann@example.com"])]
    hashed_password: str
    is_admin: bool = False
    uuid: str


class UserRead(UserBase):
    id: int

class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Passord1337!"])]

class UserCreateInternal(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(min_length=2, max_length=30, examples=["Kari Nordmann"])
    username: Optional[str] = Field(min_length=2, max_length=20, examples=["brukersen"])

class UserUpdateInternal(UserUpdate):
    updated_at: datetime.datetime

class UserDelete(UserBase):
    deleted: bool
    deleted_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

