import httpx
from google import genai
from google.genai import types

from src.app.config import get_settings
from src.core.logger import logger

settings = get_settings().gemini_settings


class VoiceService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.api_key)
        self.model_id = settings.model

    async def download_file(self, url: str) -> bytes:
        """Скачивает аудио от GreenAPI"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30.0)
            if resp.status_code == 200:
                return resp.content
            raise Exception(f"Failed to download audio: {resp.status_code}")

    async def transcribe(self, file_url: str) -> str:
        """Распознает аудио через Google Gemini"""
        try:
            if not file_url:
                return ""

            logger.info("🎤 Скачиваю голосовое сообщение...")
            audio_bytes = await self.download_file(file_url)

            logger.info("🧠 Отправляю аудио в Google Gemini...")

            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type='audio/ogg'
            )

            prompt = ("Переведи это аудио в текст."
                      " Напиши ТОЛЬКО распознанный текст, слово в слово."
                      " Без приветствий, кавычек и твоих комментариев.")

            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=[audio_part, prompt]
            )

            text = response.text.strip()
            logger.info(f"📝 Распознано: {text}")
            return text

        except Exception as e:
            logger.error(f"❌ Ошибка транскрибации: {e}")
            return ""
