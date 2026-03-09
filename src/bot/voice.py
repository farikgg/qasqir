import httpx
from groq import AsyncGroq
from src.app.config import get_settings
from src.core.logger import logger

settings = get_settings().groq_settings


class VoiceService:
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.api_key)

    async def download_file(self, url: str) -> bytes:
        """Скачивание файла (GreenAPI отдает прямую ссылку)"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30.0)
            if resp.status_code == 200:
                return resp.content
            raise Exception(f"Failed to download audio. Status: {resp.status_code}")

    async def transcribe(self, file_url: str) -> str:
        """Транскрибация через Groq Whisper"""
        try:
            if not file_url:
                return ""

            logger.info("🎤 Скачиваю голосовое...")
            audio_bytes = await self.download_file(file_url)

            logger.info("🧠 Отправляю в Whisper...")
            transcription = await self.groq_client.audio.transcriptions.create(
                file=("voice.ogg", audio_bytes),
                model="whisper-large-v3",
                response_format="json",
                temperature=0.0
            )

            text = transcription.text
            logger.info(f"📝 Распознано: {text}")
            return text

        except Exception as e:
            logger.error(f"❌ Voice Error: {e}")
            return ""