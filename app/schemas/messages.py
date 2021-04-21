from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .users import User


__all__ = (
    'Message',
)


class Message(BaseModel):
    id: int
    author: User
    text: str
    created_at: datetime

    class Config:
        orm_mode = True
