from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

from backend.src.constants import USER_PARAMS_MAX_LENGTH, MAX_EMAIL_LENGTH
from backend.src.schemas.base import ShortRecipeRead


class BaseUser(BaseModel):
    email: str = Field(
        default='artni@ya.ru',
        max_length=MAX_EMAIL_LENGTH,
        pattern='^[\w-]+@([\w-]+\.)+[\w-]{2,4}$'
    )
    username: str = Field(
        default='artni',
        max_length=USER_PARAMS_MAX_LENGTH,
        pattern=r'^[\w.@+-]+\z'
    )
    first_name: str | None = Field(
        default=None,
        max_length=USER_PARAMS_MAX_LENGTH
    )
    last_name: str | None = Field(
        default=None,
        max_length=USER_PARAMS_MAX_LENGTH
    )


class UserCreateRequest(BaseUser):
    password: str = Field(
        default='12345qwerty',
        max_length=USER_PARAMS_MAX_LENGTH
    )


class UserCreate(BaseUser):
    hashed_password: str


class UserRead(BaseUser):
    id: int


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(max_length=USER_PARAMS_MAX_LENGTH)
    new_password: str = Field(max_length=USER_PARAMS_MAX_LENGTH)

    @model_validator(mode='after')
    def check_passwords(self):
        if self.current_password == self.new_password:
            raise HTTPException(
                status_code=400,
                detail='Новый пароль должен отличаться от текущего!')
        return self


class UserWithHashedPasswordRead(UserRead):
    hashed_password: str


class UserPasswordChangeRequest(BaseModel):
    hashed_password: str


class UserCreateResponse(UserRead):
    is_subscribed: bool = False


class FollowedUserRead(UserRead):
    is_subscribed: bool = False


class FollowedUserWithRecipiesRead(FollowedUserRead):
    recipes: list[ShortRecipeRead] = []
    recipes_count: int = 0


class UserListRead(BaseModel):
    count: int
    next: str | None = None
    previous: str | None = None
    result: list[FollowedUserRead] = []
