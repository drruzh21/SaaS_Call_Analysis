import asyncio
import json
import logging
from pathlib import Path

from passlib.totp import generate_secret
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import async_session
from app.gdb import NeomodelConfig
from app.gdb.init_gdb import init_gdb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 минут
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def initNeo4j() -> None:
    try:
        NeomodelConfig().ready()
        await init_gdb()
    except Exception as e:
        logger.error(e)
        raise e


async def init() -> None:
    async with async_session() as db:
        await init_db(db)


async def main() -> None:
    logger.info("Создание начальных данных")
    await initNeo4j()
    await init()
    logger.info("Начальные данные созданы")


if __name__ == "__main__":
    asyncio.run(main())
