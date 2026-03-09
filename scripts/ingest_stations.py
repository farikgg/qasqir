import sys
import csv
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.core.database import async_session_maker
from src.services.rag_service import RagService
from src.core.logger import logger

CSV_PATH = BASE_DIR / "data/locations.csv"


async def ingest():
    logger.info("🚀 Начинаем загрузку станций в векторную базу...")

    async with async_session_maker() as session:
        rag = RagService(session)

        docs_to_add = []

        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("Наименование")
                    if not name: continue

                    content = f"""
                        СТАНЦИЯ: {name}
                        АДРЕС: {row.get('Адрес', '')}
                        ТИП ПОРТОВ: {row.get('Порт1')} / {row.get('Порт2')}
                        МОЩНОСТЬ: {row.get('MaxPwr')} кВт
                        ОПИСАНИЕ: {row.get('Описание станции', '')}
                        ТАРИФ: {row.get('Тариф', '')}
                        ПРОБЛЕМЫ: {row.get('Проблемы', '')}
                        """
                    docs_to_add.append(content)

            logger.info(f"📦 Найдено {len(docs_to_add)} станций. Генерируем векторы...")
            await rag.add_documents(docs_to_add)
            logger.info("✅ Все станции успешно загружены в базу!")

        except FileNotFoundError:
            logger.error(f"❌ Файл {CSV_PATH} не найден!")

if __name__ == "__main__":
    asyncio.run(ingest())
