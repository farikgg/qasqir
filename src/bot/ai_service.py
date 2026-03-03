from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import SecretStr

from src.app.config import get_settings
from src.core.models import Message
from src.bot.prompt import SYSTEM_PROMPT

settings = get_settings().groq_settings


class LangChainService:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        self.llm = ChatGroq(
            temperature=0.3,
            model=settings.model,
            api_key=settings.api_key
        )

    async def get_history_messages(self, limit=6):
        """Загружаем историю из Postgres и конвертируем в объекты LangChain"""
        result = await self.db.execute(
            select(Message)
            .where(Message.user_id == self.user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        db_msgs = result.scalars().all()[::-1]

        lc_messages = []
        for msg in db_msgs:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "ai":
                lc_messages.append(AIMessage(content=msg.content))

        return lc_messages

    async def save_message(self, role: str, content: str):
        """Сохраняем в БД"""
        msg = Message(user_id=self.user_id, role=role, content=content)
        self.db.add(msg)
        await self.db.commit()

    async def generate_response(self, user_text: str) -> str:
        # Сохраняем вопрос пользователя
        await self.save_message("user", user_text)

        # Подготовка промпта
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # Получаем историю
        history = await self.get_history_messages()

        # Создаем цепочку
        chain = prompt | self.llm

        try:
            response = await chain.ainvoke({
                "history": history,
                "input": user_text
            })
            ai_text = response.content

        except Exception as e:
            print(f"❌ Groq Error: {e}")
            return "Извините, сейчас высокая нагрузка на сеть. Попробуйте позже или позовите менеджера."

        await self.save_message("ai", ai_text)

        return ai_text
