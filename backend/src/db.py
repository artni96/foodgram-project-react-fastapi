from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (Mapped, declarative_base, declared_attr,
                            mapped_column)

from backend.src.config import settings


engine = create_async_engine(settings.DB_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
session = async_session_maker()


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.split('model')[0].lower()
    id: Mapped[int] = mapped_column(primary_key=True)


Base = declarative_base(cls=PreBase)


async def get_async_session():
    async with session:
        yield session
