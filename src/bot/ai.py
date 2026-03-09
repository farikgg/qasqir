from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.app.config import get_settings
from src.core.models import Message, User
from src.core.logger import logger
from src.bot.prompt import SYSTEM_PROMPT_TEMPLATE

settings = get_settings().groq_settings


class LangChainService:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.llm = ChatGroq(
            temperature=0.4,
            model_name=settings.model,
            api_key=settings.api_key
        )

    async def get_history_messages(self, limit=10):
        """История переписки"""
        result = await self.db.execute(
            select(Message)
            .where(Message.user_id == self.user.phone_number)
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
        msg = Message(user_id=self.user.phone_number, role=role, content=content)
        self.db.add(msg)
        await self.db.commit()

    async def generate_response(self, user_text: str, is_system_instruction=False) -> str:
        """
        is_system_instruction=True используется для генерации приветствия от имени бота,
        когда мы просим его 'Поздоровайся'.
        """
        if not is_system_instruction:
            await self.save_message("user", user_text)

        formatted_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            user_name=self.user.name or "Друг",
            language="Русский" if self.user.language == "ru" else "Казахский"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", formatted_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        history = await self.get_history_messages()

        chain = prompt | self.llm

        try:
            response = await chain.ainvoke({
                "history": history,
                "input": user_text
            })
            ai_text = response.content

        except Exception as e:
            logger.error(f"❌ Groq Error: {e}")
            return "Извините, я задумался. Повторите вопрос?"

        await self.save_message("ai", ai_text)
        return ai_text
