import sys
import csv
import asyncio

from pathlib import Path
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.core.database import async_session_maker
from src.core.logger import logger
from src.services.rag_service import RagService

CSV_PATH = BASE_DIR / "data/locations.csv"
TXT_PATH = BASE_DIR / "data/charger_type.txt"


async def ingest():
    logger.info("🚀 Начинаем загрузку знаний в векторную базу...")

    async with async_session_maker() as session:
        rag = RagService(session)

        # Очищаем старые данные, чтобы не было дублей при перезапуске скрипта
        await session.execute(text("TRUNCATE TABLE knowledge_chunks RESTART IDENTITY;"))
        await session.commit()

        docs_to_add = []

        # ЗАГРУЗКА СТАНЦИЙ (CSV)
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("Наименование")
                    if not name: continue

                    content = f"""
                        [ТИП: СТАНЦИЯ ЗАРЯДКИ]
                        НАЗВАНИЕ: {name}
                        АДРЕС: {row.get('Адрес', '')}
                        ПОРТЫ: {row.get('Порт1')} / {row.get('Порт2')}
                        МОЩНОСТЬ: {row.get('MaxPwr')} кВт
                        ОПИСАНИЕ: {row.get('Описание станции', '')}
                        ТАРИФ: {row.get('Тариф', '')}
                        ПРОБЛЕМЫ: {row.get('Проблемы', '')}
                    """
                    docs_to_add.append(content.strip())
            logger.info(f"📦 Прочитано станций: {len(docs_to_add)}")
        except FileNotFoundError:
            logger.error(f"❌ Файл {CSV_PATH} не найден!")

        # ЗАГРУЗКА ТЕХНИЧЕСКИХ ПРАВИЛ (TXT)
        try:
            if TXT_PATH.exists():
                with open(TXT_PATH, mode='r', encoding='utf-8') as f:
                    tech_text = f.read().strip()
                    if tech_text:
                        # Оборачиваем текст, чтобы ИИ понимал контекст
                        tech_content = f"[ТИП: ТЕХНИЧЕСКАЯ БАЗА ЗНАНИЙ И ОГРАНИЧЕНИЯ]\n{tech_text}"
                        docs_to_add.append(tech_content)
                        logger.info("📦 Прочитан файл технических правил (charger_type.txt)")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения {TXT_PATH}: {e}")

        # ГЕНЕРАЦИЯ ВЕКТОРОВ И СОХРАНЕНИЕ
        if docs_to_add:
            logger.info(f"🧠 Генерируем векторы для {len(docs_to_add)} блоков (это займет время)...")
            await rag.add_documents(docs_to_add)
            logger.info("✅ Все знания успешно загружены в базу!")
        else:
            logger.error("⚠️ Нет данных для загрузки.")

if __name__ == "__main__":
    asyncio.run(ingest())
