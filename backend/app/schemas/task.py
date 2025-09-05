from datetime import date, datetime

from sqlmodel import SQLModel, Field

from app.utils.security import generate_uid


class Task(SQLModel):
    date: date = Field(primary_key=True, default=date.today())
    points: int = Field(default=10)
