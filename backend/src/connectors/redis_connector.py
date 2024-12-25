import redis.asyncio as redis
from loguru import logger


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        self.redis = await redis.Redis(host=self.host, port=self.port)
        logger.info("Успешное поключение к Redis")

    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        return await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            logger.info("Успешное отключение от Redis")
