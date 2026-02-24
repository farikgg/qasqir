import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import User
from src.schemas.webhook_schema import WebhookEventDTO, OutgoingMessageDTO
from src.app.config import get_settings
from src.bot.answers import Texts, BUTTONS

settings = get_settings()


class BotLogic:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(self, chat_id: str, text: str, buttons: list = None):
        """Упрощенная отправка"""
        dto = OutgoingMessageDTO(chat_id=chat_id, message=text, buttons=buttons)
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{settings.gateway_url}/send", json=dto.model_dump())
            except Exception as e:
                print(f"❌ Gateway Error: {e}")

    # --- ХЕЛПЕРЫ ---
    def get_text(self, user: User, key_ru: str, key_kz: str, **kwargs):
        """Выбирает текст по языку юзера"""
        template = key_ru if user.language == "ru" else key_kz
        return template.format(**kwargs)

    async def get_or_create_user(self, user_id: str) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            user = User(phone_number=user_id, state="START")
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    # --- ГЛАВНАЯ ЛОГИКА ---
    async def process_event(self, event: WebhookEventDTO):
        user = await self.get_or_create_user(event.user_id)

        # 0. ГЛОБАЛЬНАЯ НАВИГАЦИЯ (Кнопка "Назад" или "Меню")
        if event.content == "nav_back":
            user.state = "MAIN_MENU"
            # Пробрасываем вниз, чтобы сразу отобразить меню

        # 1. START
        if user.state == "START":
            # Если язык и имя уже есть - сразу в меню (Запоминание)
            if user.language and user.name:
                user.state = "MAIN_MENU"
                # Идем дальше, не делаем return
            else:
                btns = [BUTTONS["LANG_KZ"], BUTTONS["LANG_RU"]]
                await self.send(user.phone_number, Texts.WELCOME, btns)
                user.state = "WAITING_LANG"
                await self.db.commit()
                return

        # 2. ВЫБОР ЯЗЫКА
        if user.state == "WAITING_LANG":
            if event.content == "lang_ru":
                user.language = "ru"
            elif event.content == "lang_kz":
                user.language = "kz"
            else:
                # Если прислали текст вместо кнопки
                await self.send(user.phone_number, Texts.WELCOME, [BUTTONS["LANG_KZ"], BUTTONS["LANG_RU"]])
                return

            user.state = "WAITING_NAME"
            msg = self.get_text(user, Texts.ASK_NAME_RU, Texts.ASK_NAME_KZ)
            await self.send(user.phone_number, msg)
            await self.db.commit()
            return

        # 3. ВВОД ИМЕНИ
        if user.state == "WAITING_NAME":
            user.name = event.content  # Сохраняем имя
            user.state = "MAIN_MENU"
            # Сразу показываем меню (переход к следующему блоку)

        # 4. ГЛАВНОЕ МЕНЮ
        if user.state == "MAIN_MENU":
            # Обработка выбора из меню
            if event.content == "main_problem":
                user.state = "MENU_PROBLEM"
                msg = self.get_text(user, Texts.PROBLEM_HEAD_RU, Texts.PROBLEM_HEAD_KZ)
                btns = [BUTTONS["PROB_BATTERY"], BUTTONS["PROB_VIDEO"], BUTTONS["PROB_OTHER"], BUTTONS["BACK"]]
                await self.send(user.phone_number, msg, btns)

            elif event.content == "main_payment":
                user.state = "MENU_PAYMENT"
                msg = self.get_text(user, Texts.PAYMENT_HEAD_RU, Texts.PAYMENT_HEAD_KZ)
                btns = [BUTTONS["PAY_KASPI"], BUTTONS["PAY_REFUND"], BUTTONS["BACK"]]
                await self.send(user.phone_number, msg, btns)

            elif event.content == "main_store":
                user.state = "MENU_STORE"
                msg = self.get_text(user, Texts.STORE_HEAD_RU, Texts.STORE_HEAD_KZ)
                btns = [BUTTONS["STORE_RFID"], BUTTONS["STORE_HOME"], BUTTONS["BACK"]]
                await self.send(user.phone_number, msg, btns)

            elif event.content == "main_app":
                # Просто шлем ссылки и кнопку "Спасибо/Меню"
                msg = self.get_text(user, Texts.APP_LINKS_RU, Texts.APP_LINKS_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["FINISH"], BUTTONS["BACK"]])

            elif event.content == "main_manager":
                msg = self.get_text(user, Texts.MANAGER_WAIT_RU, Texts.MANAGER_WAIT_KZ)
                await self.send(user.phone_number, msg)
                # Тут можно отправлять алерт в Telegram админам

            else:
                # Показываем само Меню
                msg = self.get_text(user, Texts.GREETING_RU, Texts.GREETING_KZ, name=user.name)
                btns = [
                    BUTTONS["MAIN_PROBLEM"],
                    BUTTONS["MAIN_PAYMENT"],
                    BUTTONS["MAIN_STORE"],
                    BUTTONS["MAIN_APP"],
                    BUTTONS["MAIN_MANAGER"]
                ]
                await self.send(user.phone_number, msg, btns)

            await self.db.commit()
            return

        # 5. ПОДМЕНЮ: ПРОБЛЕМЫ
        if user.state == "MENU_PROBLEM":
            if event.content == "prob_battery":
                msg = self.get_text(user, Texts.LOW_BATTERY_RU, Texts.LOW_BATTERY_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["FINISH"], BUTTONS["BACK"]])

            elif event.content == "prob_video":
                msg = self.get_text(user, Texts.VIDEO_INSTRUCTION_RU, Texts.VIDEO_INSTRUCTION_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["FINISH"], BUTTONS["BACK"]])

            elif event.content == "prob_other":
                msg = self.get_text(user, Texts.MANAGER_WAIT_RU, Texts.MANAGER_WAIT_KZ)
                await self.send(user.phone_number, msg)
                # Логика вызова менеджера

            elif event.content == "nav_finish":
                await self.finish_conversation(user)
                return

        # 6. ПОДМЕНЮ: ОПЛАТА
        if user.state == "MENU_PAYMENT":
            if event.content == "pay_kaspi":
                msg = self.get_text(user, Texts.KASPI_RU, Texts.KASPI_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["FINISH"], BUTTONS["BACK"]])

            elif event.content == "pay_refund":
                msg = self.get_text(user, Texts.REFUND_RU, Texts.REFUND_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["FINISH"], BUTTONS["BACK"]])

            elif event.content == "nav_finish":
                await self.finish_conversation(user)
                return

        # 7. ПОДМЕНЮ: МАГАЗИН
        if user.state == "MENU_STORE":
            if event.content == "store_rfid":
                msg = self.get_text(user, Texts.RFID_RU, Texts.RFID_KZ)
                # В конце можно добавить кнопку "Хочу купить"
                await self.send(user.phone_number, msg, [BUTTONS["MAIN_MANAGER"], BUTTONS["BACK"]])

            elif event.content == "store_home":
                msg = self.get_text(user, Texts.HOME_STATION_RU, Texts.HOME_STATION_KZ)
                await self.send(user.phone_number, msg, [BUTTONS["MAIN_MANAGER"], BUTTONS["BACK"]])

            elif event.content == "nav_finish":
                await self.finish_conversation(user)
                return

        # Обработка кнопки "Спасибо, всё" в любом другом месте
        if event.content == "nav_finish":
            await self.finish_conversation(user)

    async def finish_conversation(self, user: User):
        """Завершает диалог, прощается и возвращает в Главное Меню"""
        msg = self.get_text(user, Texts.GOODBYE_RU, Texts.GOODBYE_KZ)
        await self.send(user.phone_number, msg)

        # Сбрасываем стейт на МЕНЮ (чтобы при следующем "Привет" не спрашивал имя)
        user.state = "MAIN_MENU"
        await self.db.commit()
