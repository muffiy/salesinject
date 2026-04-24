from fastapi import APIRouter, Request, HTTPException
from ....services import telegram_service

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    if "message" in update:
        msg = update["message"]
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = msg.get("text", "")

        if not chat_id:
            return {"ok": True}

        if text == "/start":
            await telegram_service.send_message(
                chat_id,
                "Welcome to SalesInject! 🚀\nYour AI-powered sales assistant."
            )
            await telegram_service.send_mini_app_button(chat_id)

        elif text == "/help":
            await telegram_service.send_message(
                chat_id,
                "Commands:\n/start - Start the bot\n/missions - View available tasks (coming soon)"
            )

    return {"ok": True}
