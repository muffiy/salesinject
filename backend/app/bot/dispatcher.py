from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from app.core.config import settings

bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
dp = Dispatcher()
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    from app.bot.keyboards import get_launch_keyboard
    await message.answer(
        "🚀 *Welcome to SalesInject!*\n\n"
        "Turn content into campaigns. Claim bounties. Conquer the map.\n\n"
        "Use /scout <niche> <location> to find influencers\n"
        "Use /generate <prompt> to create content ideas\n"
        "Tap below to open the War Room ⬇️",
        parse_mode="Markdown",
        reply_markup=get_launch_keyboard(),
    )


@router.message(Command("scout"))
async def cmd_scout(message: Message):
    from app.tasks import run_scout_mission

    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer("Usage: /scout <niche> <location>\nExample: /scout fashion Tunis")
        return

    niche = args[0]
    location = " ".join(args[1:])
    user_id = str(message.from_user.id)
    chat_id = message.chat.id

    await message.answer(f"🔍 Launching scout mission for *{niche}* in *{location}*...", parse_mode="Markdown")
    run_scout_mission.delay(niche, location, user_id, chat_id)


@router.message(Command("generate"))
async def cmd_generate(message: Message):
    from app.tasks import generate_ad_idea

    prompt = message.text.replace("/generate ", "").strip()
    if not prompt:
        await message.answer("Usage: /generate <prompt>\nExample: /generate viral hook for coffee shop in Tunis")
        return

    user_id = str(message.from_user.id)
    await message.answer("✨ Generating content ideas...")
    generate_ad_idea.delay(user_id, prompt)


@router.message(Command("offers"))
async def cmd_offers(message: Message):
    await message.answer(
        "📍 *Active Offers*\n\n"
        "Open the Mini App to see offers on the map!\n"
        "Claim bounties, complete tasks, earn TND 💰",
        parse_mode="Markdown",
    )


dp.include_router(router)
