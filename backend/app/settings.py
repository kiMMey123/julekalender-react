import dotenv
from os import environ

dotenv_file = dotenv.find_dotenv()
print(dotenv_file)
dotenv.load_dotenv(dotenv_file)

def get_env_var(var_name, default=None):
    env_var = environ.get(f"JULEKALENDER_{var_name}")
    return default if env_var is None else env_var

JULEKALENDER_ANSWER_KEY=get_env_var("ANSWER_KEY").encode("utf-8")

ATTEMPTS_PER_RESET = 10

SCORES_PER_HINT_USED = {
    0: 10,
    1: 7,
    2: 5,
    3: 3,
    4: 2,
    5: 1
}