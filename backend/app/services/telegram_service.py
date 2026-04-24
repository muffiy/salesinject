import httpx
from ..core.config import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}"

async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        response.raise_for_status()
        return response.json()

async def send_mini_app_button(chat_id: int):
    keyboard = {
        "inline_keyboard": [[
            {"text": "🚀 Open SalesInject", "web_app": {"url": settings.MINI_APP_URL}}
        ]]
    }
    await send_message(chat_id, "Click below to open the app:", keyboard)

async def set_webhook(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/setWebhook", params={"url": url})
        return response.json()
