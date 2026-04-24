from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

router = APIRouter(prefix="/seed", tags=["Seed"])

@router.post("/")
def seed_database(db: Session = Depends(get_db)):
    # Create initial missions/tasks
    tasks = [
        models.Task(title="Sell FitPro E-Book", description="Create a TikTok selling the new FitPro program.", niche="fitness", reward_amount=15.00),
        models.Task(title="Local Gym Lead Gen", description="Get 5 people to sign up for a local gym trial in Tunis.", niche="fitness", reward_amount=50.00),
        models.Task(title="Tech Gadget Unboxing", description="Unbox and review the newest EDC smart watch.", niche="tech", reward_amount=20.00)
    ]
    db.add_all(tasks)
    db.commit()
    return {"status": "success", "message": "Database seeded with initial missions!"}
