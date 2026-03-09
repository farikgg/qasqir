import csv
import os

from pathlib import Path

from src.bot.answers import TextRu
from src.core.logger import logger

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "data/locations.csv"


class KnowledgeBaseService:
    @staticmethod
    def get_general_info() -> str:
        return f"""
            === СПРАВКА ===
            {TextRu.APP_LINKS}
            {TextRu.LOW_BATTERY}
            {TextRu.KASPI}
            {TextRu.REFUND}
            {TextRu.RFID}
            {TextRu.HOME_STATION}
            """

    @staticmethod
    def get_stations_info() -> str:
        if not os.path.exists(CSV_PATH):
            logger.error(f"❌ Файл {CSV_PATH} не найден!")
            return "Список станций временно недоступен (технический сбой)."

        stations_text = "=== СПИСОК СТАНЦИЙ QASQIR (Ищи здесь по улицам и названиям) ===\n"
        count = 0

        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("Наименование")
                    if not name: continue

                    addr = row.get("Адрес", "Нет адреса")
                    desc = row.get("Описание станции", "").replace("\n", " ")

                    stations_text += f"- {name} | Адрес: {addr} | Порты: {row.get('Порт1')}/{row.get('Порт2')} | Инфо: {desc}\n"
                    count += 1

            logger.info(f"✅ Загружено {count} станций в базу знаний.")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения CSV: {e}")
            return "Ошибка базы данных."

        return stations_text

    @staticmethod
    def build_knowledge_base() -> str:
        return KnowledgeBaseService.get_general_info() + "\n" + KnowledgeBaseService.get_stations_info()
