from redis.asyncio import Redis

from web_app.config.settings import settings


class RedisHelper:
    def __init__(self, host: str, port: int, expire: int) -> None:
        self.redis = Redis(host=host, port=port, decode_responses=True)
        self.expire = expire

    async def set(self, key: str, value: str, expire: int = None) -> None:
        await self.redis.set(key, value, ex=expire or self.expire)

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def rpush(self, key: str, value: str) -> None:
        await self.redis.rpush(key, value)

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        return await self.redis.lrange(key, start, end)

    async def sadd(self, key: str, value: str) -> None:
        await self.redis.sadd(key, value)

    async def close(self) -> None:
        await self.redis.close()


redis_helper = RedisHelper(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT,
    expire=settings.redis.EXPIRE_SECONDS
)
