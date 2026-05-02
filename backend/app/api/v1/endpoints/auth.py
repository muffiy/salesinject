from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
import urllib.parse
import hmac
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User

router = APIRouter()

class TelegramAuth(BaseModel):
    initData: str

def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    parsed_data = urllib.parse.parse_qsl(init_data)
    data_dict = {k: v for k, v in parsed_data}
    hash_value = data_dict.pop('hash', None)
    
    if not hash_value:
        return None
        
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data_dict.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hash != hash_value:
        return None
    return data_dict

@router.post("/telegram")
def auth_telegram(data: TelegramAuth, db: Session = Depends(get_db)):
    if not settings.BOT_TOKEN:
        # For local development without token
        import json
        try:
            parsed = urllib.parse.parse_qsl(data.initData)
            user_data_str = dict(parsed).get('user', '{}')
            user_data = json.loads(user_data_str)
        except:
            user_data = {"id": 12345, "username": "dev_user"}
    else:
        auth_data = verify_telegram_init_data(data.initData, settings.BOT_TOKEN)
        if not auth_data:
            raise HTTPException(status_code=401, detail="Invalid Telegram data")
        import json
        user_data = json.loads(auth_data.get('user', '{}'))

    telegram_id = user_data.get('id')
    username = user_data.get('username')
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    token_expires = datetime.utcnow() + timedelta(days=7)
    token = jwt.encode(
        {"user_id": str(user.id), "exp": token_expires},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer", "user": {"id": str(user.id), "username": user.username}}
