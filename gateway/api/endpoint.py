import httpx

from fastapi import APIRouter, HTTPException

from gateway.app.config import get_settings
from gateway.core.logger import logger
from gateway.schemas.schemas import GreenWebhookData, CoreMessageDTO, OutgoingMessageDTO
from gateway.green_api.client import client as green_client

router = APIRouter(tags=["Webhook Gateway"])
settings = get_settings().green_api


@router.post("/webhook")
async def receive_webhook(payload: GreenWebhookData):
    """
    Принимает вебхук от GreenAPI -> Конвертирует -> Шлет в Core
    """
    if payload.typeWebhook != "incomingMessageReceived":
        return {"status": "ignored", "reason": "not_incoming_message"}

    try:
        sender_data = payload.senderData or {}
        sender_raw = sender_data.get("chatId", "")
        user_id = sender_raw.replace("@c.us", "")

        if not user_id:
            return {"status": "ignored", "reason": "no_chat_id"}

        message_data = payload.messageData or {}
        msg_type = message_data.get("typeMessage")

        content = ""
        final_type = "text"

        if msg_type == "textMessage":
            text_data = message_data.get("textMessageData", {})
            content = text_data.get("textMessage", "")

        elif msg_type == "extendedTextMessage":
            text_data = message_data.get("extendedTextMessageData", {})
            content = text_data.get("text", "")

        elif msg_type == "interactiveButtonsResponse":
            btn_data = message_data.get("interactiveButtonsResponse", {})
            content = btn_data.get("selectedButtonId") or btn_data.get("selectedId")
            final_type = "button_reply"

        elif msg_type == "buttonsResponseMessage":
            btn_data = message_data.get("buttonsResponseMessage", {})
            content = btn_data.get("selectedButtonId")
            final_type = "button_reply"

        elif msg_type == "listResponseMessage":
            list_data = message_data.get("listResponseMessage", {})
            content = list_data.get("selectedRowId")
            final_type = "button_reply"

        else:
            logger.info(f"⚠️ Unknown message type: {msg_type}")
            return {"status": "ignored", "reason": f"unsupported_type_{msg_type}"}

        if not content:
            logger.info(f"⚠️ Empty content for type {msg_type}. Data: {message_data}")
            return {"status": "error", "reason": "empty_content"}

        dto = CoreMessageDTO(
            user_id=user_id,
            message_type=final_type,
            content=content,
            timestamp=payload.timestamp
        )

        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{settings.core_url}/event", json=dto.model_dump())
            except httpx.ConnectError:
                logger.info("❌ Core service is unavailable!")

        return {"status": "ok", "forwarded_to_core": True}

    except Exception as e:
        logger.info(f"❌ CRITICAL ERROR: {e}")
        logger.info(f"🧨 BAD PAYLOAD: {payload.model_dump_json()}")
        return {"status": "error", "detail": str(e)}


@router.post("/send")
async def send_message(message: OutgoingMessageDTO):
    try:
        if message.buttons:
            result = await green_client.send_buttons(message.chat_id, message.message, message.buttons)
        else:
            result = await green_client.send_text(message.chat_id, message.message)

        return {"status": "sent", "provider_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
