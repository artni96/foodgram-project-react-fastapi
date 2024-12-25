from backend.src.connectors.redis_connector import RedisManager
from backend.src.config import settings


redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
