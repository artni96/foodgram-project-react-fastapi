from pydantic import BaseModel, ConfigDict

from backend.src.schemas.users import FollowedUserWithRecipiesRead


class SubscriptionCreate(BaseModel):
    author_id: int
    subscriber_id: int

    model_config = ConfigDict(from_attributes=True)


class SubscriptionListRead(BaseModel):
    count: int
    next: str | None = "test123"
    previous: str | None = "test123"
    results: list[FollowedUserWithRecipiesRead] = []
