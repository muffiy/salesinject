import uuid
from datetime import datetime, timezone
from app.models.models import User, Offer, OfferClaim
from app.services.mission_service import claim_mission, check_geofence, resolve_competition, finalize_mission


def test_claim_mission(session):
    brand = User(id=uuid.uuid4(), telegram_id=101, first_name="BrandM", role="brand")
    influencer = User(id=uuid.uuid4(), telegram_id=102, first_name="InfM", role="creator")
    session.add_all([brand, influencer])
    session.commit()

    offer = Offer(
        id=uuid.uuid4(),
        brand_id=brand.id,
        title="Mission Offer",
        lat=36.8065,
        lon=10.1815,
    )
    session.add(offer)
    session.commit()

    claim = claim_mission(session, str(influencer.id), str(offer.id))
    assert claim is not None
    assert claim.status == "claimed"
    assert claim.offer_id == offer.id


def test_check_geofence(session):
    brand = User(id=uuid.uuid4(), telegram_id=201, first_name="BrandG")
    influencer = User(id=uuid.uuid4(), telegram_id=202, first_name="InfG")
    session.add_all([brand, influencer])
    session.commit()

    offer = Offer(id=uuid.uuid4(), brand_id=brand.id, title="Geo Offer", lat=36.80, lon=10.18)
    session.add(offer)
    session.commit()

    claim = OfferClaim(id=uuid.uuid4(), offer_id=offer.id, influencer_id=influencer.id, status="claimed")
    session.add(claim)
    session.commit()

    result = check_geofence(session, str(claim.id), 36.80, 10.18)
    assert result is True
    updated = session.query(OfferClaim).filter_by(id=claim.id).first()
    assert updated.status == "arrived"


def test_resolve_competition(session):
    brand = User(id=uuid.uuid4(), telegram_id=301, first_name="BrandC")
    inf1 = User(id=uuid.uuid4(), telegram_id=302, first_name="InfC1")
    inf2 = User(id=uuid.uuid4(), telegram_id=303, first_name="InfC2")
    session.add_all([brand, inf1, inf2])
    session.commit()

    offer = Offer(id=uuid.uuid4(), brand_id=brand.id, title="Comp Offer", lat=36.80, lon=10.18)
    session.add(offer)
    session.commit()

    c1 = OfferClaim(id=uuid.uuid4(), offer_id=offer.id, influencer_id=inf1.id, status="completed")
    c2 = OfferClaim(id=uuid.uuid4(), offer_id=offer.id, influencer_id=inf2.id, status="claimed")
    session.add_all([c1, c2])
    session.commit()
    c1.completed_at = datetime.now(timezone.utc)
    session.commit()

    result = resolve_competition(session, str(c1.id))
    assert "winner" in result
    assert "position" in result


def test_finalize_mission(session):
    brand = User(id=uuid.uuid4(), telegram_id=401, first_name="BrandF")
    inf = User(id=uuid.uuid4(), telegram_id=402, first_name="InfF")
    session.add_all([brand, inf])
    session.commit()

    offer = Offer(id=uuid.uuid4(), brand_id=brand.id, title="Finalize Offer", lat=36.80, lon=10.18)
    session.add(offer)
    session.commit()

    claim = OfferClaim(id=uuid.uuid4(), offer_id=offer.id, influencer_id=inf.id)
    session.add(claim)
    session.commit()

    finalize_mission(session, str(claim.id), 75.0, 1)
    updated = session.query(OfferClaim).filter_by(id=claim.id).first()
    assert updated.status == "completed"
    assert updated.payout_amount == 75.0
    assert updated.position == 1