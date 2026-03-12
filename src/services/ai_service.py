from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.app.config import get_settings
from src.bot.prompt import SYSTEM_PROMPT_TEMPLATE, NAME_EXTRACTION_PROMPT
from src.bot.knowledge import KnowledgeBaseService
from src.services.rag_service import RagService
from src.core.models import Message, User
from src.core.logger import logger

settings = get_settings().gemini_settings


class LangChainService:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.llm = ChatGoogleGenerativeAI(
            api_key=settings.api_key,
            model=settings.model,
            temperature=0.3
        )
        self.knowledge_base = KnowledgeBaseService.build_knowledge_base()

    async def get_history_messages(self, limit=5):
        result = await self.db.execute(
            select(Message)
            .where(Message.user_id == self.user.phone_number)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        db_msgs = result.scalars().all()[::-1]
        lc_messages = []

        for msg in db_msgs:
            if msg.role == "user": lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "ai": lc_messages.append(AIMessage(content=msg.content))
        return lc_messages

    async def save_message(self, role: str, content: str):
        msg = Message(user_id=self.user.phone_number, role=role, content=content)
        self.db.add(msg)
        await self.db.commit()

    async def generate_response(self, user_text: str, is_system_instruction=False) -> str:
        if not is_system_instruction:
            await self.save_message("user", user_text)

        rag = RagService(self.db)
        found_stations = await rag.search(user_text, limit=3)

        rag_context = found_stations if found_stations else "Нет информации о конкретных станциях по этому запросу."

        full_knowledge = f"{self.knowledge_base}\n\nНАЙДЕННЫЕ СТАНЦИИ:\n{rag_context}"

        formatted_system = SYSTEM_PROMPT_TEMPLATE.format(
            user_name=self.user.name or "Друг",
            language="Русский" if self.user.language == "ru" else "Казахский",
            knowledge_base=full_knowledge
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", formatted_system),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        history = await self.get_history_messages()
        chain = prompt | self.llm

        try:
            response = await chain.ainvoke({"history": history, "input": user_text})
            ai_text = response.content
        except Exception as e:
            logger.error(f"❌ Groq Chat Error: {e}")
            return "Сервис с ИИ временно недоступен. Извиняемся за неудобство 😔"

        await self.save_message("ai", ai_text)
        return ai_text

    async def extract_name(self, text: str) -> str:
        """Возвращает имя или None"""
        prompt = NAME_EXTRACTION_PROMPT.format(user_text=text)

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content.strip().replace(".", "")  # Чистим от точек

            if "NONE" in result or len(result) > 20:
                return None
            return result
        except Exception as e:
            logger.error(f"❌ Groq Extraction Error: {e}")
            return None
