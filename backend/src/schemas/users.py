from typing import Generic

from fastapi_users import models, schemas
from fastapi_users.schemas import PYDANTIC_V2, model_dump
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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


class UserCreate(BaseUserCreate):
    email: EmailStr = Field(default='artni@ya.ru')
    password: str = Field(default='12345qwerty')
    username: str = Field(max_length=32, default='artni')
    first_name: str | None = Field(default=None, max_length=32)
    last_name: str | None = Field(default=None, max_length=32)


class BaseUser(CreateUpdateDictModel, Generic[models.ID]):
    """Base User model."""

    id: models.ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    if PYDANTIC_V2:  # pragma: no cover
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:  # pragma: no cover

        class Config:
            orm_mode = True


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
    # is_subscribed: bool | None = False


class UserUpdate(schemas.BaseUserUpdate):
    username: str = Field(max_length=64)
    first_name: str | None = Field(default=None, max_length=64)
    last_name: str | None = Field(default=None, max_length=128)


class SubscriptionCreate(BaseModel):
    author_id: int
    subscriber_id: int

    model_config = ConfigDict(from_attributes=True)
