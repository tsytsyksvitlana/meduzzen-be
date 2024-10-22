import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web_app.core.config import config
from web_app.db.postgres_helper import postgres_helper
from web_app.db.redis_helper import redis_helper
from web_app.routers.healthcheck import router as router

logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Starting up...")
#
#     await postgres_helper.engine.connect()
#     logger.info("PostgreSQL connected.")
#
#     await redis_helper.redis.ping()
#     logger.info("Redis connected.")
#
#     yield
#
#     await postgres_helper.dispose()
#     logger.info("PostgreSQL connection closed.")
#
#     await redis_helper.close()
#     logger.info("Redis connection closed.")


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.include_router(router)

origins = [
    f"http://{config.server_host}:{config.server_port}",
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
        app,
        host=config.server_host,
        port=config.server_port,
        reload=config.reload,
    )
