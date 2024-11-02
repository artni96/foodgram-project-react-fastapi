from fastapi_users import schemas
from fastapi_users.schemas import model_dump
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from fastapi import HTTPException


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(default='artni@ya.ru', max_length=254)
    password: str = Field(default='12345qwerty', max_length=150)
    username: str = Field(default='artni', max_length=150)
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=254)
    hashed_password: str
    username: str = Field(max_length=150)
    first_name: str | None = Field(max_length=150)
    last_name: str | None = Field(max_length=150)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str = Field(max_length=32)
    first_name: str | None = Field(default=None, max_length=32)
    last_name: str | None = Field(default=None, max_length=32)


class ExpendedUserRead(UserRead):
    is_subscribed: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    username: str = Field(max_length=64)
    first_name: str | None = Field(default=None, max_length=64)
    last_name: str | None = Field(default=None, max_length=128)


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(max_length=150)
    new_password: str = Field(max_length=150)

    @model_validator(mode='after')
    def check_passwords(self):
        if self.current_password == self.new_password:
            raise HTTPException(
                status_code=400,
                detail='Новый пароль должен отличаться от текущего!')


class UserWithHashedPasswordRead(UserRead):
    hashed_password: str


class UserPasswordChangeRequest(BaseModel):
    hashed_password: str


class FollowedUserRead(UserRead):
    is_subscribed: bool = True
