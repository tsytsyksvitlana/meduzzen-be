from redis.asyncio import Redis

from web_app.config.settings import settings


class RedisHelper:
    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host=host, port=port, decode_responses=True)

    async def set(self, key: str, value: str) -> None:
        await self.redis.set(key, value)

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def close(self) -> None:
        await self.redis.close()


redis_helper = RedisHelper(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT
)
