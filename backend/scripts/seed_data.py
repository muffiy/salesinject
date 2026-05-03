import random
import uuid
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import User, Offer, OfferClaim, OfferPerformance, PayoutTransaction, MissionShare


def seed() -> None:
    db = SessionLocal()
    try:
        brand = User(
            id=uuid.uuid4(),
            username="brand_test",
            role="brand",
            reputation_score=320,
            level=2,
            xp=640,
        )
        db.add(brand)

        influencers = []
        for i in range(1, 6):
            user = User(
                id=uuid.uuid4(),
                username=f"influencer_{i}",
                role="creator",
                reputation_score=random.randint(50, 800),
                level=random.randint(1, 4),
                xp=random.randint(10, 1200),
            )
            db.add(user)
            influencers.append(user)

        db.commit()

        offers = []
        for i in range(3):
            reward = random.randint(10, 25)
            offer = Offer(
                id=uuid.uuid4(),
                brand_id=brand.id,
                title=f"Test Offer {i + 1}",
                description="Visit this place and upload a short proof video",
                lat=36.8065 + (random.random() - 0.5) * 0.02,
                lon=10.1815 + (random.random() - 0.5) * 0.02,
                bounty_value=reward,
                auto_boost=random.choice([True, False]),
                status="active",
                max_claims=10,
                expires_at=datetime.now(timezone.utc) + timedelta(days=2),
            )
            db.add(offer)
            offers.append(offer)

        db.commit()

        for offer in offers:
            claim = OfferClaim(
                id=uuid.uuid4(),
                offer_id=offer.id,
                influencer_id=influencers[0].id,
                status="completed",
                boosted=False,
                payout_amount=float(offer.bounty_value or 0),
                claimed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(3, 24)),
                completed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 2)),
            )
            db.add(claim)
            db.commit()

            db.add(PayoutTransaction(
                user_id=influencers[0].id,
                claim_id=claim.id,
                amount=claim.payout_amount,
                status="completed",
            ))

            db.add(OfferPerformance(
                claim_id=claim.id,
                views=random.randint(100, 1500),
                clicks=random.randint(5, 100),
                conversions=random.randint(0, 20),
            ))

            db.add(MissionShare(
                user_id=influencers[0].id,
                mission_id=claim.id,
                bonus_granted=True,
            ))

        db.commit()
        print("Seed data inserted successfully")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
