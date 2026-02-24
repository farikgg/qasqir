from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.app.config import get_settings
from src.core.database import async_engine
from src.api import endpoint as core_router
from src.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск Core...")
    logger.info("Core запущен!")
    yield

    logger.info("Остановка Core...")
    await async_engine.dispose()
    logger.info("✅ Core остановлен")

def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug
    )
    application.include_router(core_router.router)

    return application

app = create_application()
