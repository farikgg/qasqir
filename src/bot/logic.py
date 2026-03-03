import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import User
from src.core.logger import logger
from src.schemas.webhook_schema import WebhookEventDTO, OutgoingMessageDTO
from src.app.config import get_settings
from src.bot.answers import TextRu, TextKz, ButtonIDs
from src.bot.ai_service import LangChainService

settings = get_settings()


class BotLogic:
    def __init__(self, db: AsyncSession):
        self.db = db

    def get_texts(self, user: User):
        if user.language == "kz":
            return TextKz
        return TextRu

    def make_btns(self, texts_class, *ids):
        buttons = []
        for btn_id in ids:
            btn_text = texts_class.BUTTONS.get(btn_id, "Button")
            buttons.append({"id": btn_id, "text": btn_text})
        return buttons

    async def send(self, chat_id: str, text: str, buttons: list = None):
        dto = OutgoingMessageDTO(chat_id=chat_id, message=text, buttons=buttons)
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

    async def finish_conversation(self, user: User):
        texts = self.get_texts(user)
        await self.send(user.phone_number, texts.GOODBYE)
        user.state = "MAIN_MENU"
        await self.db.commit()

    # --- ГЛАВНАЯ ЛОГИКА ---
    async def process_event(self, event: WebhookEventDTO):
        try:
            user = await self.get_or_create_user(event.user_id)
            T = self.get_texts(user)

            # ГЛОБАЛЬНЫЕ КНОПКИ
            if event.content == ButtonIDs.BACK:
                user.state = "MAIN_MENU"

            if event.content == ButtonIDs.FINISH and user.state != "AI_CHAT":
                await self.finish_conversation(user)
                return

            # 1. СТАРТ
            if user.state == "START":
                if user.language and user.name:
                    user.state = "MAIN_MENU"
                else:
                    btns = self.make_btns(TextRu, ButtonIDs.LANG_KZ, ButtonIDs.LANG_RU)
                    await self.send(user.phone_number, TextRu.WELCOME, btns)
                    user.state = "WAITING_LANG"
                    await self.db.commit()
                    return

            # 2. ЯЗЫК
            if user.state == "WAITING_LANG":
                if event.content == ButtonIDs.LANG_RU:
                    user.language = "ru"
                elif event.content == ButtonIDs.LANG_KZ:
                    user.language = "kz"
                else:
                    btns = self.make_btns(TextRu, ButtonIDs.LANG_KZ, ButtonIDs.LANG_RU)
                    await self.send(user.phone_number, TextRu.WELCOME, btns)
                    return

                T = self.get_texts(user)
                user.state = "WAITING_NAME"
                await self.send(user.phone_number, T.ASK_NAME)
                await self.db.commit()
                return

            # 3. ИМЯ
            if user.state == "WAITING_NAME":
                user.name = event.content
                user.state = "MAIN_MENU"

            # 4. ГЛАВНОЕ МЕНЮ (3 КАТЕГОРИИ)
            if user.state == "MAIN_MENU":

                # --- НАВИГАЦИЯ ПО КАТЕГОРИЯМ ---

                # Категория 1: Зарядка
                if event.content == ButtonIDs.CAT_CHARGE:
                    # 2 функции + Назад = 3 кнопки (ИДЕАЛЬНО)
                    btns = self.make_btns(T, ButtonIDs.MAIN_PROBLEM, ButtonIDs.MAIN_PAYMENT, ButtonIDs.BACK)
                    await self.send(user.phone_number, T.MENU_CHARGE, btns)

                # Категория 2: Сервисы
                elif event.content == ButtonIDs.CAT_SERVICE:
                    # 2 функции + Назад = 3 кнопки
                    btns = self.make_btns(T, ButtonIDs.MAIN_STORE, ButtonIDs.MAIN_APP, ButtonIDs.BACK)
                    await self.send(user.phone_number, T.MENU_SERVICE, btns)

                # Категория 3: Помощь
                elif event.content == ButtonIDs.CAT_HELP:
                    # 2 функции + Назад = 3 кнопки
                    btns = self.make_btns(T, ButtonIDs.MAIN_AI_HELP, ButtonIDs.MAIN_MANAGER, ButtonIDs.BACK)
                    await self.send(user.phone_number, T.MENU_HELP, btns)


                # --- ОБРАБОТКА ФУНКЦИЙ ---

                elif event.content == ButtonIDs.MAIN_PROBLEM:
                    user.state = "MENU_PROBLEM"
                    btns = self.make_btns(T, ButtonIDs.PROB_BATTERY, ButtonIDs.PROB_VIDEO, ButtonIDs.PROB_OTHER)
                    await self.send(user.phone_number, T.PROBLEM_HEAD, btns)
                    await self.send(user.phone_number, "...", self.make_btns(T, ButtonIDs.BACK))

                elif event.content == ButtonIDs.MAIN_PAYMENT:
                    user.state = "MENU_PAYMENT"
                    # 3 кнопки: Kaspi, Refund, Back -> ВЛЕЗАЕТ В ОДНО!
                    btns = self.make_btns(T, ButtonIDs.PAY_KASPI, ButtonIDs.PAY_REFUND, ButtonIDs.BACK)
                    await self.send(user.phone_number, T.PAYMENT_HEAD, btns)

                elif event.content == ButtonIDs.MAIN_STORE:
                    user.state = "MENU_STORE"
                    # 3 кнопки: RFID, Home, Back -> ВЛЕЗАЕТ В ОДНО!
                    btns = self.make_btns(T, ButtonIDs.STORE_RFID, ButtonIDs.STORE_HOME, ButtonIDs.BACK)
                    await self.send(user.phone_number, T.STORE_HEAD, btns)

                elif event.content == ButtonIDs.MAIN_APP:
                    await self.send(user.phone_number, T.APP_LINKS, self.make_btns(T, ButtonIDs.FINISH, ButtonIDs.BACK))

                elif event.content == ButtonIDs.MAIN_MANAGER:
                    await self.send(user.phone_number, T.MANAGER_WAIT)

                elif event.content == ButtonIDs.MAIN_AI_HELP:
                    user.state = "AI_CHAT"
                    await self.send(user.phone_number, T.AI_START, self.make_btns(T, ButtonIDs.BACK))

                # ДЕФОЛТ: КОРЕНЬ МЕНЮ
                else:
                    msg = T.GREETING.format(name=user.name)
                    # 3 Кнопки -> ВЛЕЗАЕТ В ОДНО!
                    btns = self.make_btns(T, ButtonIDs.CAT_CHARGE, ButtonIDs.CAT_SERVICE, ButtonIDs.CAT_HELP)
                    await self.send(user.phone_number, msg, btns)

                await self.db.commit()
                return

            # --- ПОДМЕНЮ (КОНТЕНТ) ---

            # 5. ПРОБЛЕМЫ
            if user.state == "MENU_PROBLEM":
                if event.content == ButtonIDs.PROB_BATTERY:
                    await self.send(user.phone_number, T.LOW_BATTERY,
                                    self.make_btns(T, ButtonIDs.FINISH, ButtonIDs.BACK))
                elif event.content == ButtonIDs.PROB_VIDEO:
                    await self.send(user.phone_number, T.VIDEO_INSTRUCTION,
                                    self.make_btns(T, ButtonIDs.FINISH, ButtonIDs.BACK))
                elif event.content == ButtonIDs.PROB_OTHER:
                    user.state = "AI_CHAT"
                    await self.send(user.phone_number, T.AI_START, self.make_btns(T, ButtonIDs.BACK))
                    await self.db.commit()
                    return

            # 6. ОПЛАТА
            if user.state == "MENU_PAYMENT":
                if event.content == ButtonIDs.PAY_KASPI:
                    await self.send(user.phone_number, T.KASPI, self.make_btns(T, ButtonIDs.FINISH, ButtonIDs.BACK))
                elif event.content == ButtonIDs.PAY_REFUND:
                    await self.send(user.phone_number, T.REFUND, self.make_btns(T, ButtonIDs.FINISH, ButtonIDs.BACK))

            # 7. МАГАЗИН
            if user.state == "MENU_STORE":
                if event.content == ButtonIDs.STORE_RFID:
                    await self.send(user.phone_number, T.RFID,
                                    self.make_btns(T, ButtonIDs.MAIN_MANAGER, ButtonIDs.BACK))
                elif event.content == ButtonIDs.STORE_HOME:
                    await self.send(user.phone_number, T.HOME_STATION,
                                    self.make_btns(T, ButtonIDs.MAIN_MANAGER, ButtonIDs.BACK))

            # 8. AI
            if user.state == "AI_CHAT":
                if event.message_type == "text":
                    ai = LangChainService(self.db, user.phone_number)
                    response_text = await ai.generate_response(event.content)
                    if "TRANSFER_TO_MANAGER" in response_text:
                        await self.send(user.phone_number, T.MANAGER_WAIT)
                        user.state = "MAIN_MENU"
                    else:
                        await self.send(user.phone_number, response_text, self.make_btns(T, ButtonIDs.BACK))
                elif event.message_type != "button_reply":
                    await self.send(user.phone_number, "✍️...", self.make_btns(T, ButtonIDs.BACK))

            await self.db.commit()

        except Exception as error:
            logger.error(f"🔥 CRITICAL ERROR: {error}")
            import traceback
            logger.error(traceback.format_exc())