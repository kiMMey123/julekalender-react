from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uuid


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password:str) -> str:
    return "fakehashed" + password

def fake_decode_password(password:str) -> bool:
    return password == fake_hash_password(password)

def generate_user_id() -> str:
    return str(uuid.uuid4())