import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import get_settings
from src.services.ai_service import LangChainService
from src.bot.voice import VoiceService
from src.core.models import User
from src.core.logger import logger
from src.schemas.webhook_schema import WebhookEventDTO, OutgoingMessageDTO

settings = get_settings()


class BotLogic:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(self, chat_id: str, text: str):
        """Отправка ТОЛЬКО текста (без кнопок)"""
        dto = OutgoingMessageDTO(chat_id=chat_id, message=text, buttons=None)
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{settings.gateway_url}/send", json=dto.model_dump())
            except Exception as e:
                logger.error(f"❌ Gateway Error: {e}")

    async def get_or_create_user(self, user_id: str) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            user = User(phone_number=user_id, state="START")
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def process_event(self, event: WebhookEventDTO):
        try:
            user = await self.get_or_create_user(event.user_id)
            user_text = ""

            if event.message_type == "text":
                user_text = event.content

            elif event.message_type == "voice":
                voice_service = VoiceService()
                recognized_text = await voice_service.transcribe(event.content)

                if recognized_text:
                    user_text = recognized_text
                    logger.info(f"🎤 Звук транскрибирован: {user_text}")
                else:
                    await self.send(user.phone_number, "Не удалось разобрать голосовое,"
                                                       " попробуйте текстовым сообщением, пожалуйста 🙏")
                    return

            ai = LangChainService(self.db, user)

            if not user.name:
                if user.state == "START":
                    greeting_prompt = (f"Пользователь написал: '{user_text}'. "
                                       f"Поздоровайся на этом же языке, представься как Qasqir AI и вежливо спроси,"
                                       f" как к нему обращаться.")

                    response = await ai.generate_response(greeting_prompt, is_system_instruction=True)
                    await self.send(user.phone_number, response)

                    user.state = "WAITING_NAME"
                    await self.db.commit()
                    return

                if user.state == "WAITING_NAME":
                    extracted_name = await ai.extract_name(user_text)

                    if extracted_name:
                        user.name = extracted_name
                        user.state = "CHAT_MODE"
                        await self.db.commit()

                        response = await ai.generate_response(user_text)
                        await self.send(user.phone_number, response)
                    else:
                        retry_prompt = (f"Пользователь написал: '{user_text}'."
                                        f" Мы ждали имя, но не поняли его."
                                        f" Вежливо попроси представиться еще раз, чтобы мы могли помочь.")
                        response = await ai.generate_response(retry_prompt, is_system_instruction=True)
                        await self.send(user.phone_number, response)
                    return

            else:
                response = await ai.generate_response(user_text)

                if "[CALL_MANAGER]" in response:
                    clean_text = response.replace("[CALL_MANAGER]", "").strip()
                    if clean_text:
                        await self.send(user.phone_number, clean_text)

                    await self.send(user.phone_number, "Подключаю оператора... 👨‍💻")
                    # TODO: Send Telegram Alert
                else:
                    await self.send(user.phone_number, response)

        except Exception as error:
            logger.error(f"🔥 CRITICAL ERROR: {error}")
            import traceback
            logger.error(traceback.format_exc())
