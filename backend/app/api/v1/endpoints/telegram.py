from fastapi import APIRouter, Request
from ....services.telegram_service import send_message, send_mini_app_button

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive Telegram bot updates via webhook (alternative to polling)."""
    update = await request.json()

    if "message" in update:
        msg = update["message"]
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = msg.get("text", "")

        if not chat_id:
            return {"ok": True}

        if text == "/start":
            await send_message(
                chat_id,
                "🚀 *Welcome to SalesInject!*\n\n"
                "Turn everyday content into viral campaigns.\n"
                "Claim bounties. Conquer the map.\n\n"
                "Tap below to launch the War Room ⬇️",
            )
            await send_mini_app_button(chat_id)

        elif text == "/help":
            await send_message(
                chat_id,
                "📋 *Commands:*\n\n"
                "/start — Launch the bot\n"
                "/scout <niche> <location> — Find influencers\n"
                "/generate <prompt> — Create content ideas\n"
                "/offers — View active offers\n"
                "/help — Show this message",
            )

        elif text.startswith("/scout"):
            from ....tasks import run_scout_mission
            args = text.split()[1:]
            if len(args) < 2:
                await send_message(chat_id, "Usage: /scout <niche> <location>")
            else:
                niche = args[0]
                location = " ".join(args[1:])
                run_scout_mission.delay(niche, location, str(chat_id), chat_id)
                await send_message(chat_id, f"🔍 Scouting {niche} in {location}...")

        elif text.startswith("/generate"):
            from ....tasks import generate_ad_idea
            prompt = text.replace("/generate ", "")
            generate_ad_idea.delay(str(chat_id), prompt)
            await send_message(chat_id, "✨ Generating content ideas...")

    return {"ok": True}
