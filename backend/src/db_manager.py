from backend.src.repositories.ingredients import IngredientRepository
from backend.src.repositories.subscriptions import SubscriptionRepository
from backend.src.repositories.tags import TagRepository
from backend.src.repositories.users import UserRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.subscriptions = SubscriptionRepository(self.session)
        self.ingredients = IngredientRepository(self.session)
        self.tags = TagRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
