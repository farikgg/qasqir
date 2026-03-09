import asyncio
import csv
import sys
import re
from pathlib import Path
from sqlalchemy import select

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.core.logger import logger
from src.core.database import async_session_maker
from src.core.models import User

def clean_phone(phone: str) -> str:
    clean = re.sub(r'\D', '', phone)
    if len(clean) == 11 and clean.startswith('8'):
        clean = '7' + clean[1:]
    return clean

async def import_from_csv(filename: str):
    logger.info(f"📂 Читаем файл: {filename}...")

    async with async_session_maker() as session:
        try:
            with open(filename, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                count_new = 0
                count_updated = 0

                for row in reader:
                    raw_phone = row['phone'].strip()
                    name = row['name'].strip()
                    lang = row['language'].strip().lower()  # ru или kz

                    if not raw_phone:
                        continue

                    clean_number = clean_phone(raw_phone)

                    stmt = select(User).where(User.phone_number == clean_number)
                    result = await session.execute(stmt)
                    user = result.scalar_one_or_none()

                    if user:
                        user.name = name
                        user.language = lang
                        if user.state in ["START", "WAITING_LANG", "WAITING_NAME"]:
                            user.state = "MAIN_MENU"
                        logger.info(f"🔄 Обновлен: {clean_number} ({name})")
                        count_updated += 1
                    else:
                        new_user = User(
                            phone_number=clean_number,
                            name=name,
                            language=lang,
                            state="MAIN_MENU"
                        )
                        session.add(new_user)
                        logger.info(f"✅ Добавлен: {clean_number} ({name})")
                        count_new += 1

            await session.commit()
            logger.info("-" * 30)
            logger.info(f"🎉 Готово! Добавлено: {count_new}, Обновлено: {count_updated}")

        except FileNotFoundError:
            logger.error(f"❌ Файл {filename} не найден в корне проекта!")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(import_from_csv("data/users.csv"))
