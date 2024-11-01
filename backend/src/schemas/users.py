from fastapi_users import schemas
from fastapi_users.schemas import model_dump
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from fastapi import HTTPException
from http import HTTPStatus


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return model_dump(self, exclude_unset=True, exclude={"id"})


class BaseUserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str


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


class UserRead(schemas.BaseUser[int]):
    email: EmailStr
    username: str = Field(max_length=32)
    first_name: str | None = Field(default=None, max_length=32)
    last_name: str | None = Field(default=None, max_length=32)


class BaseUserRead(BaseModel):
    id: int
    email: EmailStr
    username: str = Field(max_length=32)
    first_name: str | None = Field(default=None, max_length=32)
    last_name: str | None = Field(default=None, max_length=32)


class ExpendedUserRead(BaseUserRead):
    is_subscribed: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    username: str = Field(max_length=64)
    first_name: str | None = Field(default=None, max_length=64)
    last_name: str | None = Field(default=None, max_length=128)


class SubscriptionCreate(BaseModel):
    author_id: int
    subscriber_id: int

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_author_isnt_subscriber(self):
        if self.author_id == self.subscriber_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Пользователь не может подписаться на себя!'
            )


class SubscriptionResponse(SubscriptionCreate):
    id: int
