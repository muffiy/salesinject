from app.bot.dispatcher import dp, bot
from app.core.config import settings
import asyncio

async def start_bot():
    if bot and not settings.USE_WEBHOOK:
        asyncio.create_task(dp.start_polling(bot))

async def stop_bot():
    if bot:
        await bot.session.close()
