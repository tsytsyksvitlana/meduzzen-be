import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web_app.config.settings import settings
from web_app.db.postgres_helper import postgres_helper
from web_app.db.redis_helper import redis_helper
from web_app.routers.healthcheck import router as router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    await postgres_helper.engine.connect()
    logger.info("PostgreSQL connected.")

    await redis_helper.redis.ping()
    logger.info("Redis connected.")

    yield

    await postgres_helper.dispose()
    logger.info("PostgreSQL connection closed.")

    await redis_helper.close()
    logger.info("Redis connection closed.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)

origins = [
    f"http://{settings.fastapi.SERVER_HOST}:{settings.fastapi.SERVER_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "web_app.main:app",
        host=settings.fastapi.SERVER_HOST,
        port=settings.fastapi.SERVER_PORT,
        reload=settings.fastapi.SERVER_RELOAD,
    )
