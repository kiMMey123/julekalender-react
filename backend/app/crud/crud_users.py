from fastcrud import FastCRUD

from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserDelete, UserUpdateInternal

CRUDUser = FastCRUD[User, UserCreate, UserUpdate, UserUpdateInternal, UserDelete, UserRead]
crud_users = CRUDUser(User)