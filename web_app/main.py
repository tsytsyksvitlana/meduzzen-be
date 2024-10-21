import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web_app.core.config import config
from web_app.routers.healthcheck import router as router

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
