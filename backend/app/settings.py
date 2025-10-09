import dotenv
from os import environ

from pydantic.v1 import BaseSettings
from starlette.config import Config

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
config = Config(dotenv_file)


def get_env_var(var_name, default=None):
    env_var = environ.get(f"JULEKALENDER_{var_name}")
    if env_var is None:
        print(f"{var_name} not set")
    return default if env_var is None else env_var

class Settings(BaseSettings):
    ANSWER_KEY = get_env_var("ANSWER_KEY").encode("utf-8")
    SECRET_KEY = get_env_var("SECRET_KEY")
    ADMIN_NAME = get_env_var("ADMIN_NAME")
    ADMIN_USERNAME = get_env_var("ADMIN_USERNAME")
    ADMIN_EMAIL = get_env_var("ADMIN_EMAIL")
    ADMIN_PASSWORD = get_env_var("ADMIN_PASSWORD")

    ATTEMPTS_PER_RESET = 10
    SCORES_PER_HINT_USED = {
        0: 10,
        1: 7,
        2: 5,
        3: 3,
        4: 2,
        5: 1
    }

settings = Settings()



