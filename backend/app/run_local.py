import asyncio
import logging

import uvicorn
from sqlalchemy import text

from app.backend_pre_start import main as init_db
from app.core.config import settings
from app.db.session import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_db_connection(max_retries=5, retry_delay=2):
    logger.info(f"Testing database connection to {settings.SQLALCHEMY_DATABASE_URI}")
    
    for attempt in range(max_retries):
        try:
            async with async_session() as db:
                result = await db.execute(text("SELECT 1"))
                logger.info(f"Database test query result: {result.scalar()}")
                logger.info("Database connection successful!")
                return True
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not connect to database.")
                return False

async def main():
    # Вывод настроек подключения
    logger.info("Database connection settings:")
    logger.info(f"Server: {settings.POSTGRES_SERVER}")
    logger.info(f"Port: {settings.POSTGRES_PORT}")
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"User: {settings.POSTGRES_USER}")
    logger.info(f"SQLAlchemy URI: {settings.SQLALCHEMY_DATABASE_URI}")

    # Проверка подключения к БД
    if not await test_db_connection():
        logger.error("Failed to connect to database. Check your settings.")
        exit(1)

    try:
        # Инициализация БД
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully!")

        # Запуск сервера
        logger.info("Starting FastAPI server...")
        config = uvicorn.Config(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            workers=1
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())