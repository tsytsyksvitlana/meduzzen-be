import uvicorn
from web_app.routers.routers import router as router
from web_app.core.config import config
from fastapi import FastAPI


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        reload=config.reload,
    )
