from pydantic import BaseModel
from typing import Optional


class CoreMessageDTO(BaseModel):
    """Gateway -> Core"""
    user_id: str
    message_type: str
    content: str
    timestamp: int


class OutgoingMessageDTO(BaseModel):
    """Gateway -> Outgoing"""
    chat_id: str
    message: str
    buttons: Optional[list[dict]] = None


class GreenWebhookData(BaseModel):
    """ВХОДЯЩИЙ ВЕБХУК ОТ GREEN API"""
    typeWebhook: str
    instanceData: dict
    timestamp: int
    idMessage: str
    senderData: Optional[dict] = None
    messageData: Optional[dict] = None

    class Config:
        extra = "ignore"