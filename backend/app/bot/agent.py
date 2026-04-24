import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from app.bot.keyboards import get_launch_keyboard
from app.core.config import settings

logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handler for the /start command."""
    welcome_text = (
        "<b>Welcome to SalesInject Command.</b>\n"
        "Your terminal is ready. Click below to initialize your first operative."
    )
    await message.answer(
        text=welcome_text,
        reply_markup=get_launch_keyboard(),
        parse_mode="HTML"
    )

@dp.message()
async def fallback_handler(message: types.Message):
    """Fallback handler for text messages."""
    await message.answer("Use the button above to launch the Command Center.")
