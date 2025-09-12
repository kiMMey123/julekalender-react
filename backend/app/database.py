from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel


db_file_name = "test.db"
db_url = "sqlite:///" + db_file_name

connect_args = {"check_same_thread": False}
engine = create_engine(db_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@contextmanager
def session_scope():
    session = SessionDep
    try:
        with Session(engine) as session:
            yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

