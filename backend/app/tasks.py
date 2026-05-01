"""
Celery Tasks — background jobs for SalesInject.

All DB-touching tasks create their own session from SessionLocal
to avoid session-sharing issues across Celery worker processes.
"""
from datetime import datetime, timezone
from app.worker import celery_app
from app.core.database import SessionLocal


@celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
def run_scout_mission(self, niche: str, location: str, user_id: str, chat_id: int = None):
    """Full scout mission pipeline — Exa search → LLM analysis → save → notify."""
    from app.services.paperclip_agent import run_scout_mission as execute_mission

    db = SessionLocal()
    try:
        result = execute_mission(
            user_id=user_id,
            niche=niche,
            location=location,
            chat_id=chat_id,
            db=db,
        )
        return result
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=1)
def generate_ad_idea(self, user_id: str, prompt: str):
    """Generate AI-powered content ideas using RAG pipeline."""
    from app.tools.paperclip_tools import generate_ad_idea_tool

    db = SessionLocal()
    try:
        result = generate_ad_idea_tool(user_id=user_id, prompt=prompt, db=db)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@celery_app.task
def expire_offers():
    """Mark expired offers as 'expired' — runs every 15 minutes via Beat."""
    from app.models import Offer

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        expired = (
            db.query(Offer)
            .filter(Offer.status == "active", Offer.expires_at != None, Offer.expires_at < now)
            .all()
        )
        for offer in expired:
            offer.status = "expired"
        db.commit()
        print(f"[Beat] Expired {len(expired)} offers")
        return {"expired_count": len(expired)}
    finally:
        db.close()


@celery_app.task
def send_offer_alerts(offer_id: str):
    """Push Telegram notification to nearby influencers when a new offer is created."""
    import asyncio
    from app.models import Offer, User
    from app.services.telegram_service import send_message

    db = SessionLocal()
    try:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if not offer:
            return {"status": "offer_not_found"}

        # Find active creators (simplified — in production use PostGIS proximity)
        creators = db.query(User).filter(User.role == "creator", User.telegram_id != None).limit(50).all()

        sent = 0
        for creator in creators:
            try:
                text = (
                    f"🎯 *New Offer Available!*\n\n"
                    f"**{offer.title}**\n"
                    f"💰 Bounty: {offer.bounty_value} TND\n"
                    f"🏷️ Discount: {offer.discount_value}%\n\n"
                    f"Open the app to claim! ⚡"
                )
                asyncio.run(send_message(creator.telegram_id, text))
                sent += 1
            except Exception:
                continue

        return {"alerts_sent": sent}
    finally:
        db.close()


@celery_app.task
def process_payout(claim_id: str):
    """Process payout for a completed offer claim — creates PayoutTransaction."""
    from app.models import OfferClaim, Offer, User, PayoutTransaction
    from app.core.config import settings

    db = SessionLocal()
    try:
        claim = db.query(OfferClaim).filter(OfferClaim.id == claim_id).first()
        if not claim or claim.status != "completed":
            return {"status": "invalid_claim"}

        offer = db.query(Offer).filter(Offer.id == claim.offer_id).first()
        if not offer:
            return {"status": "offer_not_found"}

        user = db.query(User).filter(User.id == claim.influencer_id).first()
        if not user:
            return {"status": "user_not_found"}

        # Calculate payout (bounty minus platform commission)
        bounty = float(offer.bounty_value or 0)
        commission = bounty * settings.PLATFORM_COMMISSION_RATE
        payout_amount = bounty - commission

        # Create transaction record
        txn = PayoutTransaction(
            user_id=user.id,
            claim_id=claim.id,
            amount=payout_amount,
            currency="TND",
            status="pending",
        )
        db.add(txn)

        # Credit user's wallet
        user.wallet_balance = float(user.wallet_balance or 0) + payout_amount
        user.total_earnings = float(user.total_earnings or 0) + payout_amount

        db.commit()
        return {"payout_amount": payout_amount, "transaction_id": str(txn.id)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task
def rebuild_leaderboard():
    """Rebuild the leaderboard from user stats — runs hourly via Beat."""
    from app.models import User, Leaderboard
    from sqlalchemy import desc

    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .filter(User.role == "creator")
            .order_by(desc(User.total_earnings))
            .limit(100)
            .all()
        )
        for position, user in enumerate(users, 1):
            entry = db.query(Leaderboard).filter(Leaderboard.user_id == user.id).first()
            if entry:
                entry.score = float(user.total_earnings or 0)
                entry.rank_position = position
                entry.username = user.username
            else:
                entry = Leaderboard(
                    user_id=user.id,
                    username=user.username,
                    score=float(user.total_earnings or 0),
                    rank_position=position,
                )
                db.add(entry)

        db.commit()
        print(f"[Beat] Rebuilt leaderboard with {len(users)} entries")
        return {"entries": len(users)}
    finally:
        db.close()


@celery_app.task
def rank_decay():
    """Daily rank decay — inactive users lose rank points gradually."""
    from app.models import User
    from datetime import timedelta

    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        inactive = db.query(User).filter(
            User.role == "creator",
            User.last_active < cutoff,
            User.streak_days > 0,
        ).all()

        for user in inactive:
            user.streak_days = max(0, user.streak_days - 1)

        db.commit()
        print(f"[Beat] Applied rank decay to {len(inactive)} inactive users")
        return {"decayed_count": len(inactive)}
    finally:
        db.close()


@celery_app.task
def agent_learning_task(agent_id: str, submission_id: str, content_url: str):
    """Embed approved content into agent memory for future RAG improvement."""
    from app.models import AgentMemory
    from app.services.embedding_service import embed

    db = SessionLocal()
    try:
        content_text = f"Approved submission {submission_id} from URL: {content_url}"
        vector = embed(content_text)

        memory = AgentMemory(
            user_id=None,  # Will be set if we look up the agent's owner
            agent_id=agent_id,
            memory_type="learning",
            content=content_text,
            embedding=vector,
            metadata_={"source": "submission_approval", "submission_id": submission_id},
        )
        db.add(memory)
        db.commit()
        return {"status": "learned"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
