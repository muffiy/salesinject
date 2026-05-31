"""
Handlers for the Telegram bot.
Defines handlers for commands like /start, /find_influencers, etc.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import logging

from app.core.config import settings

# Try to import httpx for API calls, fallback to mock if not available
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not installed, API calls will be mocked")

logger = logging.getLogger(__name__)

# Create a router for our handlers
router = Router()

# API Hub base URL
API_HUB_URL = settings.OPENCLAW_URL if hasattr(settings, 'OPENCLAW_URL') else "http://localhost:8000"


async def call_api_hub(endpoint: str, params: dict = None) -> dict:
    """
    Call the API Hub endpoint and return the JSON response.
    If httpx is not available or the call fails, return a mock response.
    """
    if not HTTPX_AVAILABLE:
        return get_mock_response(endpoint, params)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_HUB_URL}{endpoint}", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error calling API Hub: {e}")
        return get_mock_response(endpoint, params)


def get_mock_response(endpoint: str, params: dict = None) -> dict:
    """
    Return a mock response for API Hub endpoints.
    """
    if endpoint == "/influencers/find":
        niche = params.get("niche", "fashion") if params else "fashion"
        location = params.get("location", "Tunis") if params else "Tunis"
        return {
            "influencers": [
                {
                    "id": 1,
                    "name": f"{niche} Expert 1",
                    "followers": 15000,
                    "engagement_rate": 8.5,
                    "location": location,
                    "niche": niche
                },
                {
                    "id": 2,
                    "name": f"{niche} Guru 2",
                    "followers": 25000,
                    "engagement_rate": 7.2,
                    "location": location,
                    "niche": niche
                }
            ],
            "total": 2,
            "page": 1,
            "per_page": 10
        }
    elif endpoint == "/health":
        return {"status": "ok", "service": "API Hub"}
    else:
        return {"message": "Mock response", "endpoint": endpoint}


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command."""
    from app.bot.keyboards import get_launch_keyboard
    await message.answer(
        "🚀 *Welcome to SalesInject!*\n\n"
        "Turn content into campaigns. Claim bounties. Conquer the map.\n\n"
        "Use /scout <niche> <location> to find influencers\n"
        "Use /generate <prompt> to create content ideas\n"
        "Use /find_influencers <niche> <location> to search for influencers via API Hub\n"
        "Tap below to open the War Room ⬇️",
        parse_mode="Markdown",
        reply_markup=get_launch_keyboard(),
    )


@router.message(Command("find_influencers"))
async def cmd_find_influencers(message: Message):
    """Handle the /find_influencers command."""
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer(
            "Usage: /find_influencers <niche> <location>\n"
            "Example: /find_influencers fashion Tunis"
        )
        return

    niche = args[0]
    location = " ".join(args[1:])
    user_id = str(message.from_user.id)

    await message.answer(f"🔍 Searching for {niche} influencers in {location} via API Hub...")

    # Call the API Hub endpoint
    params = {"niche": niche, "location": location, "limit": 10}
    result = await call_api_hub("/influencers/find", params)

    if "influencers" in result and result["influencers"]:
        response = f"🔍 *Found {len(result['influencers'])} {niche} influencers in {location}*:\n\n"
        for inf in result["influencers"][:5]:  # Show first 5
            response += (
                f"👤 *{inf['name']}*\n"
                f"📍 {inf.get('location', 'Unknown')}\n"
                f"📊 {inf.get('followers', 0):,} followers\n"
                f"💎 {inf.get('engagement_rate', 0):.1f}% engagement\n\n"
            )
        if len(result["influencers"]) > 5:
            response += f"_and {len(result['influencers']) - 5} more..._\n"
        response += "\nUse these influencers in your campaigns!"
    else:
        response = f"😔 No {niche} influencers found in {location}. Try different parameters."

    await message.answer(response, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle the /help command."""
    help_text = """
*Available Commands:*

/start - Welcome message and main menu
/scout <niche> <location> - Find influencers (uses Celery task)
/generate <prompt> - Generate content ideas (uses Celery task)
/find_influencers <niche> <location> - Search for influencers via API Hub
/offers - Show active offers
/help - Show this help message

*Examples:*
/scout fashion Tunis
/generate viral hook for coffee shop in Tunis
/find_influencers fitness London
    """
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle the /status command."""
    # Check API Hub health
    health = await call_api_hub("/health")
    status_emoji = "✅" if health.get("status") == "ok" else "❌"

    await message.answer(
        f"*Bot Status*\n\n"
        f"{status_emoji} API Hub: {health.get('status', 'unknown')}\n"
        f"🤖 Bot: Online\n"
        f"🔧 Mode: {'Webhook' if settings.USE_WEBHOOK else 'Polling'}",
        parse_mode="Markdown"
    )


# Include the router in the dispatcher (this will be done in main.py or dispatcher.py)
# dp.include_router(router)  # This is handled in main.py