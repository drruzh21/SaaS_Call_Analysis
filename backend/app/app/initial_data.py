import asyncio
import logging

from app.db.init_db import init_db
from app.db.session import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    logger.info("Starting database initialization from initial_data.py")
    try:
        async with async_session() as db:
            logger.info("Created database session successfully")
            await init_db(db)
            logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


async def main() -> None:
    logger.info("Создание начальных данных")
    # Инициализируем PostgreSQL
    await init()
    logger.info("Начальные данные созданы")


if __name__ == "__main__":
    asyncio.run(main())
