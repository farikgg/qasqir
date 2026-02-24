from pydantic import BaseModel
from typing import Optional, List, Dict


class WebhookEventDTO(BaseModel):
    user_id: str
    message_type: str
    content: str
    timestamp: int


class OutgoingMessageDTO(BaseModel):
    chat_id: str
    message: str
    buttons: Optional[List[Dict[str, str]]] = None
