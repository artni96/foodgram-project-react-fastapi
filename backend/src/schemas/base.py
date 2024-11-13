# from backend.src.schemas.recipes import ShortRecipeRead # noqa
# from backend.src.schemas.users import FollowedUserRead # noqa


from pydantic import BaseModel


class ShortRecipeRead(BaseModel):
    id: int
    name: str
    image: str
    cooking_time: int
