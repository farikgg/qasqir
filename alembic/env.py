import asyncio
import sys

from alembic import context
from logging.config import fileConfig
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ИМПОРТИРУЕМ КОНФИГ И МОДЕЛИ
from src.app.config import get_settings
from src.core.database import Base
from src.core.models import User


# ДОБАВЛЯЕМ SRC В ПУТЬ (чтобы alembic видел проект)
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Получаем настройки из твоего pydantic конфига
app_settings = get_settings()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# ПОДМЕНЯЕМ URL ИЗ КОНФИГА (безопаснее, чем в ini)
config.set_main_option("sqlalchemy.url", app_settings.database_settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# УКАЗЫВАЕМ METADATA (откуда брать таблицы)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
