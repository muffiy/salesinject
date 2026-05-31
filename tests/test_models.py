import uuid
from datetime import datetime, timezone
from app.models.models import User, Agent, Offer, OfferClaim, Task, PayoutTransaction


def test_create_user(session):
    user = User(
        id=uuid.uuid4(),
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        role="creator",
    )
    session.add(user)
    session.commit()

    saved = session.query(User).filter_by(telegram_id=123456789).first()
    assert saved is not None
    assert saved.username == "testuser"
    assert saved.role == "creator"
    assert saved.onboarded is False
    assert saved.xp == 0
    assert saved.level == 1


def test_create_agent(session):
    user = User(id=uuid.uuid4(), telegram_id=111, first_name="AgentOwner")
    session.add(user)
    session.commit()

    agent = Agent(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Test Scout",
        agent_type="scout",
        configuration={"niche": "fashion"},
    )
    session.add(agent)
    session.commit()

    saved = session.query(Agent).filter_by(agent_type="scout").first()
    assert saved is not None
    assert saved.name == "Test Scout"
    assert saved.is_active is True


def test_offer_claim_relationship(session):
    brand = User(id=uuid.uuid4(), telegram_id=222, first_name="Brand", role="brand")
    influencer = User(id=uuid.uuid4(), telegram_id=333, first_name="Inf", role="creator")
    session.add_all([brand, influencer])
    session.commit()

    offer = Offer(
        id=uuid.uuid4(),
        brand_id=brand.id,
        title="Test Offer",
        lat=36.8065,
        lon=10.1815,
    )
    session.add(offer)
    session.commit()

    claim = OfferClaim(
        id=uuid.uuid4(),
        offer_id=offer.id,
        influencer_id=influencer.id,
    )
    session.add(claim)
    session.commit()

    assert claim.offer.title == "Test Offer"
    assert len(offer.claims) == 1


def test_payout_transaction(session):
    user = User(id=uuid.uuid4(), telegram_id=444, first_name="PayUser")
    session.add(user)
    session.commit()

    payout = PayoutTransaction(
        id=uuid.uuid4(),
        user_id=user.id,
        amount=50.00,
        currency="TND",
        status="pending",
    )
    session.add(payout)
    session.commit()

    saved = session.query(PayoutTransaction).filter_by(user_id=user.id).first()
    assert saved.amount == 50.00
    assert saved.status == "pending"


def test_task_with_submissions(session):
    brand = User(id=uuid.uuid4(), telegram_id=555, first_name="Brand2", role="brand")
    creator = User(id=uuid.uuid4(), telegram_id=666, first_name="Creator", role="creator")
    session.add_all([brand, creator])
    session.commit()

    task = Task(
        id=uuid.uuid4(),
        brand_id=brand.id,
        title="Create a reel",
        reward_amount=100.00,
    )
    session.add(task)
    session.commit()

    from app.models.models import UserTask
    submission = UserTask(
        id=uuid.uuid4(),
        user_id=creator.id,
        task_id=task.id,
        status="submitted",
    )
    session.add(submission)
    session.commit()

    assert len(task.submissions) == 1
    assert task.submissions[0].status == "submitted"


def test_user_agent_relationship(session):
    user = User(id=uuid.uuid4(), telegram_id=777, first_name="RelUser")
    session.add(user)
    session.commit()

    agent1 = Agent(id=uuid.uuid4(), user_id=user.id, name="Agent1", agent_type="scout")
    agent2 = Agent(id=uuid.uuid4(), user_id=user.id, name="Agent2", agent_type="matchmaker")
    session.add_all([agent1, agent2])
    session.commit()

    assert len(user.agents) == 2
    assert user.agents[0].user_id == user.id