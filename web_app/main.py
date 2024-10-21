import uvicorn
from fastapi import FastAPI

from web_app.core.config import config
from web_app.routers.healthcheck import router as router

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        reload=config.reload,
    )
