"""
Onboarding Conversation Handler for Agent OS v2.
Manages the conversational onboarding flow for new users via Telegram.
"""

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, types
from aiogram.filters import Command
from app.services.memory_service import save_memory
from app.services.embedding_service import embed
import json
from uuid import uuid4


router = Router()


class OnboardingStates(StatesGroup):
    waiting_for_goal = State()
    waiting_for_niche = State()
    waiting_for_product = State()
    waiting_for_audience = State()


@router.message(Command("start_onboard"))
async def start_onboarding(message: types.Message, state: FSMContext):
    """Start the onboarding conversation."""
    await state.set_state(OnboardingStates.waiting_for_goal)
    await message.answer("What's your main goal with SalesInject? (e.g., earn money, promote my brand)")


@router.message(OnboardingStates.waiting_for_goal)
async def process_goal(message: types.Message, state: FSMContext):
    """Process the user's goal and move to niche question."""
    await state.update_data(goal=message.text)
    await state.set_state(OnboardingStates.waiting_for_niche)
    await message.answer("Which niche do you focus on? (e.g., fashion, fitness, food)")


@router.message(OnboardingStates.waiting_for_niche)
async def process_niche(message: types.Message, state: FSMContext):
    """Process the user's niche and move to product question."""
    await state.update_data(niche=message.text)
    await state.set_state(OnboardingStates.waiting_for_product)
    await message.answer("What product or service do you promote? (e.g., clothing line, fitness program)")


@router.message(OnboardingStates.waiting_for_product)
async def process_product(message: types.Message, state: FSMContext):
    """Process the user's product and move to audience question."""
    await state.update_data(product=message.text)
    await state.set_state(OnboardingStates.waiting_for_audience)
    await message.answer("Who is your target audience? (e.g., young adults, parents, entrepreneurs)")


@router.message(OnboardingStates.waiting_for_audience)
async def process_audience(message: types.Message, state: FSMContext):
    """Process the user's audience and complete onboarding."""
    # Collect all data
    data = await state.get_data()
    goal = data.get("goal")
    niche = data.get("niche")
    product = data.get("product")
    audience = message.text

    # Create user profile JSON
    user_profile = {
        "goal": goal,
        "niche": niche,
        "product": product,
        "target_audience": audience,
        "onboarded_at": str(message.date)
    }

    # Save as goal-type memory
    user_id = str(message.from_user.id)
    embedding = embed(json.dumps(user_profile))

    with SessionLocal() as db:
        memory = AgentMemory(
            user_id=user_id,
            agent_type="onboarding",
            memory_type="goal",
            content=json.dumps(user_profile),
            embedding=embedding
        )
        db.add(memory)
        db.commit()

        # Mark user as onboarded
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if user:
            user.onboarded = True
            db.commit()

    # Clear state and send welcome message
    await state.clear()

    welcome_message = (
        f"🎉 Welcome to SalesInject, {message.from_user.first_name}!\n\n"
        f"I've saved your profile:\n"
        f"• Goal: {goal}\n"
        f"• Niche: {niche}\n"
        f"• Product: {product}\n"
        f"• Audience: {audience}\n\n"
        f"You're now ready to start your first mission! Use /missions to see available tasks."
    )

    await message.answer(welcome_message)


# Import here to avoid circular imports
from ..database import SessionLocal
from ..models.models import User, AgentMemory