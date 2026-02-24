from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.webhook_schema import WebhookEventDTO
from src.bot.logic import BotLogic
from src.core.database import get_async_session

router = APIRouter(tags=["Webhook Core"])

@router.post("/event")
async def handle_event(event: WebhookEventDTO, db: AsyncSession = Depends(get_async_session)):
    """
    Сюда Gateway кидает чистые данные.
    """
    logic = BotLogic(db)
    await logic.process_event(event)
    return {"status": "processed"}
