"""
Main entry point for the Telegram bot.
Sets up the bot and starts polling.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import router as handlers_router
from app.core.config import settings

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN and settings.BOT_TOKEN != "dummy" else None
dp = Dispatcher(storage=MemoryStorage())

# Include routers
dp.include_router(handlers_router)


async def start_bot() -> None:
    """Start the bot polling."""
    if not bot:
        logger.warning("Bot token not set, skipping bot startup")
        return

    if settings.USE_WEBHOOK:
        logger.warning("Webhook mode is enabled, not starting polling")
        return

    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error while polling: {e}")
    finally:
        await bot.session.close()


async def stop_bot() -> None:
    """Stop the bot and clean up."""
    if bot:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")