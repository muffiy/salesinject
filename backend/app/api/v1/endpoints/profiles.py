"""
Profiles API — user profile management endpoints.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...deps import get_db, get_current_user
from ....models import User, Profile

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class ProfileOut(BaseModel):
    id: str
    user_id: str
    bio: Optional[str]
    avatar_url: Optional[str]
    website: Optional[str]
    location: Optional[str]
    created_at: str
    updated_at: Optional[str]

    model_config = {"from_attributes": True}


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a user profile for the authenticated user."""
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this user"
        )

    db_profile = Profile(
        user_id=current_user.id,
        bio=payload.bio,
        avatar_url=payload.avatar_url,
        website=payload.website,
        location=payload.location,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile


@router.get("/", response_model=ProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the profile for the authenticated user."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.put("/", response_model=ProfileOut)
def update_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the profile for the authenticated user."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Update fields
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile