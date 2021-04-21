from typing import Optional
from pydantic import BaseModel
from .users import User, UserRef


__all__ = (
    'Contact',
    'ContactAdd',
)


class Contact(BaseModel):
    id: int
    owner: User
    friend: User
    name: str

    class Config:
        orm_mode = True


class ContactAdd(BaseModel):
    friend: UserRef
    name: Optional[str]
