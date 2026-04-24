from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import settings

def get_launch_keyboard() -> InlineKeyboardMarkup:
    """Returns an inline keyboard with a WebApp button linking to the Mini App."""
    button = InlineKeyboardButton(
        text="LAUNCH SALESINJECT ⚡",
        url=settings.MINI_APP_URL
        # Note: If you want to use the native WebApp interface, use `web_app=WebAppInfo(url=...)`
        # But for deep links from external URLs as asked by some templates, url= works.
        # We'll use Native WebApp for true TMA experience.
    )
    # Using `web_app` makes it open inside Telegram as a TMA
    from aiogram.types.web_app_info import WebAppInfo
    tma_button = InlineKeyboardButton(
        text="LAUNCH COMMAND ⚡",
        web_app=WebAppInfo(url=settings.MINI_APP_URL)
    )
    return InlineKeyboardMarkup(inline_keyboard=[[tma_button]])
