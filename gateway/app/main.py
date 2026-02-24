from contextlib import asynccontextmanager
from fastapi import FastAPI

from gateway.app.config import get_settings
from gateway.core.logger import logger
from gateway.api import endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск Gateway...")
    logger.info("Gateway запущен!")
    yield

    logger.info("Остановка Gateway...")
    logger.info("✅ Gateway остановлен")

def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug
    )
    application.include_router(endpoint.router)

    return application

app = create_application()
