from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ... import deps
from ....models import User
from ....core.security import create_access_token, get_current_user
from ....utils.telegram import verify_telegram_data
from pydantic import BaseModel
import json

router = APIRouter()


class TelegramAuthRequest(BaseModel):
    init_data: str


@router.post("/telegram")
async def auth_telegram(
    req: TelegramAuthRequest,
    db: Session = Depends(deps.get_db)
):
    """Authenticate via Telegram Mini App initData, returns a signed JWT."""
    try:
        tg_data = verify_telegram_data(req.init_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_info = tg_data.get("user")
    if not user_info:
        raise HTTPException(status_code=400, detail="No user data provided.")

    try:
        user_data = json.loads(user_info)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in user data.")

    telegram_id = str(user_data["id"])
    username = user_data.get("username", "")
    first_name = user_data.get("first_name", "")

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            role="creator",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    Issue a fresh JWT for an already-authenticated user.
    Client should call this before the 30-minute window expires.
    The old token stays valid until its own `exp` — stateless refresh.
    """
    new_token = create_access_token(data={"user_id": str(current_user.id)})
    return {"access_token": new_token, "token_type": "bearer"}
