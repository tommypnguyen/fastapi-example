from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic.types import conint


class User(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    created_at: datetime
    email: EmailStr

    class Config:
        orm_mode = True


# Title: str, content: str
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        orm_mode = True


class PostResponse(Post):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse

    class Config:
        orm_mode = True


class PostVotes(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)
