from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.models import KnowledgeChunk

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


class RagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_documents(self, texts: list[str]):
        """Сохраняет тексты в базу (превращая в векторы)"""
        if not texts:
            return

        embeddings = embeddings_model.embed_documents(texts)

        for text, vector in zip(texts, embeddings):
            chunk = KnowledgeChunk(content=text, embedding=vector)
            self.db.add(chunk)

        await self.db.commit()

    async def search(self, query: str, limit: int = 3) -> str:
        """Ищет 3 самые похожие станции"""
        query_vector = embeddings_model.embed_query(query)

        stmt = select(KnowledgeChunk).order_by(
            KnowledgeChunk.embedding.l2_distance(query_vector)
        ).limit(limit)

        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            return ""

        return "\n---\n".join([chunk.content for chunk in chunks])
