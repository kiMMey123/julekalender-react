from fastcrud import FastCRUD

from app.models.user import User
from app.schemas.user import UserCreateInternal, UserRead, UserUpdate, UserUpdateInternal

CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdateInternal, UserUpdate, UserRead]
crud_users = CRUDUser(User)