import httpx
import json

from gateway.app.config import get_settings
from gateway.core.logger import logger

settings = get_settings().green_api


class GreenApiClient:
    def __init__(self):
        host = settings.api_host.rstrip("/")
        self.base_url = f"{host}/waInstance{settings.instance_id}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api_token}"
        }

    async def _post_request(self, method: str, payload: dict):
        url = f"{self.base_url}/{method}/{settings.api_token}"

        logger.info(f"\n📤 TRYING TO SEND TO: {url}")
        logger.info(f"📦 PAYLOAD: {json.dumps(payload, ensure_ascii=False)}\n")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                content=json.dumps(payload),
                headers=self.headers,
                timeout=20.0
            )
            logger.info(f"📩 GREEN API RESPONSE: {resp.status_code} | {resp.text}")
            return resp.json()

    async def send_text(self, chat_id: str, message: str):
        payload = {
            "chatId": f"{chat_id}@c.us",
            "message": message
        }
        return await self._post_request("sendMessage", payload)

    async def send_buttons(self, chat_id: str, message: str, buttons: list):
        formatted_buttons = [
            {"buttonId": btn["id"], "buttonText": btn["text"]}
            for btn in buttons
        ]

        payload = {
            "chatId": f"{chat_id}@c.us",
            "body": message,
            "buttons": formatted_buttons
        }

        return await self._post_request("sendInteractiveButtonsReply", payload)

client = GreenApiClient()
