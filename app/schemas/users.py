from typing import Any, Optional
import datetime
from pydantic import BaseModel
import jwt
from ..config import config


__all__ = (
    'UserCreate',
    'User',
    'UserSignIn',
    'UserSignInByName',
    'UserSignedIn',
)


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserRef(BaseModel):
    id: int

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserSignIn(BaseModel):
    email: str
    password: str


class UserSignInByName(BaseModel):
    name: str
    password: str


class UserSignedIn(User):
    id: int
    token: Optional[str]

    @classmethod
    def from_orm(cls, obj: Any) -> BaseModel:
        user = super().from_orm(obj)
        user.token = cls.generate_token(user.id)
        return user

    @classmethod
    def generate_token(cls, user_id: int) -> str:
        jwt_config = config['jwt']
        expires_at = int(datetime.datetime.utcnow().timestamp()) + int(jwt_config['duration'])
        payload = dict(exp=expires_at, user_id=user_id)
        token = jwt.encode(payload, jwt_config['secret'])
        return token

    @classmethod
    def get_user_id(cls, token: str) -> int:
        jwt_config = config['jwt']
        payload = jwt.decode(token, jwt_config['secret'], algorithms=['HS256'], options=dict(verify_exp=True))
        user_id = int(payload['user_id'])
        return user_id
