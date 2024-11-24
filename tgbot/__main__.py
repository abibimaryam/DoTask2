import asyncio
import logging

import betterlogging as bl
import orjson
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot import handlers
from tgbot.data import config

import sqlite3


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.setup())


def setup_middlewares(dp: Dispatcher) -> None:
    pass


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_handlers(dp)
    setup_middlewares(dp)


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


def create_db():
    try:
        conn = sqlite3.connect('links.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            category TEXT,
            priority INTEGER,
            source TEXT
        )''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"General error: {e}")


async def main():
    setup_logging()
    session = AiohttpSession(
        json_loads=orjson.loads,
    )

    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()

    dp = Dispatcher(
        storage=storage,
    )
    create_db()
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
