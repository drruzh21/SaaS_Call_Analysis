import logging
import time
import uvicorn
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.config import settings
from app.backend_pre_start import main as init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_connection(max_retries=5, retry_delay=2):
    logger.info(f"Testing database connection to {settings.SQLALCHEMY_DATABASE_URI}")
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT 1")).fetchone()
            logger.info(f"Database test query result: {result}")
            db.close()
            logger.info("Database connection successful!")
            return True
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not connect to database.")
                return False

if __name__ == "__main__":
    # Не используем os.environ.update(), так как переменные уже установлены в PyCharm
    # Просто запускаем приложение с настройками из PyCharm

    # Вывод настроек подключения
    logger.info("Database connection settings:")
    logger.info(f"Server: {settings.POSTGRES_SERVER}")
    logger.info(f"Port: {settings.POSTGRES_PORT}")
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"User: {settings.POSTGRES_USER}")
    logger.info(f"SQLAlchemy URI: {settings.SQLALCHEMY_DATABASE_URI}")

    # Проверка подключения к БД
    if not test_db_connection():
        logger.error("Failed to connect to database. Check your settings.")
        exit(1)

    try:
        # Инициализация БД
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully!")

        # Запуск сервера
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            workers=1
        )
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise