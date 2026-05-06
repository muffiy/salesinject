import hmac
import hashlib
import time
from urllib.parse import parse_qsl
from ..core.config import settings

def verify_telegram_data(init_data: str) -> dict:
    """
    Verify that the initData from Telegram Mini App is authentic.
    Returns the parsed data as dict if valid, otherwise raises ValueError.
    """
    parsed = dict(parse_qsl(init_data))
    if "hash" not in parsed:
        raise ValueError("Missing hash")

    received_hash = parsed["hash"]
    data_check_parts = []
    for key in sorted(parsed.keys()):
        if key != "hash":
            data_check_parts.append(f"{key}={parsed[key]}")
    data_check_string = "\n".join(data_check_parts)

    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if computed_hash != received_hash:
        if settings.ALLOW_INSECURE_TG_INIT_DATA:
            return parsed
        raise ValueError("Hash mismatch")

    # Optional replay protection if auth_date is present.
    auth_date_raw = parsed.get("auth_date")
    if auth_date_raw:
        try:
            auth_date = int(auth_date_raw)
            now = int(time.time())
            if now - auth_date > settings.TELEGRAM_INITDATA_MAX_AGE_SECONDS:
                if settings.ALLOW_INSECURE_TG_INIT_DATA:
                    return parsed
                raise ValueError("initData expired")
        except ValueError:
            if not settings.ALLOW_INSECURE_TG_INIT_DATA:
                raise ValueError("Invalid auth_date")

    return parsed
