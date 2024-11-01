from pydantic import BaseModel, ConfigDict, model_validator
from fastapi import HTTPException, status


class SubscriptionCreate(BaseModel):
    author_id: int
    subscriber_id: int

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_author_isnt_subscriber(self):
        if self.author_id == self.subscriber_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пользователь не может подписаться на себя!'
            )


class SubscriptionResponse(SubscriptionCreate):
    id: int
