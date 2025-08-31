from redis import Redis
from functools import lru_cache
from app.core.config import settings

@lru_cache
def get_redis_client():
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True  # So you get strings instead of bytes
    )
