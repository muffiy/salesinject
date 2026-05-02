"""
Agent Market for Agent OS v2.

Implements performance-based agent selection with staking economy.
Agents are ranked by success rate, speed, and stake amount.
"""

import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import SessionLocal
from ..models_agent_os import AgentRanking, AgentStake
from ..agent_os.event_bus import emit_agent_performance


def calculate_score(agent_name: str, db: Optional[Session] = None) -> float:
    """
    Calculate performance score for an agent.

    Score formula:
        (success_rate * 0.5) + (speed_score * 0.2) + (stake_score * 0.2) - (failure_rate * 0.1)

    Args:
        agent_name: Name of the agent
        db: Optional database session (creates new if None)

    Returns:
        Performance score between 0.0 and 1.0 (higher is better)
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        stats = db.query(AgentRanking).filter_by(agent_name=agent_name).first()

        if not stats:
            # Default score for new agents
            return 0.5

        # Normalize speed: 0ms = 1.0, 1000ms = 0.0, clipped
        speed_norm = 1.0 - min(1.0, stats.avg_speed_ms / 1000.0)

        # Normalize stake: 0 = 0.0, 1000 = 1.0, logarithmic scaling
        stake_norm = min(1.0, stats.stake / 1000.0)

        # Calculate weighted score
        score = (
            stats.success_rate * 0.5 +
            speed_norm * 0.2 +
            stake_norm * 0.2 -
            stats.failure_rate * 0.1
        )

        # Clip to valid range
        return max(0.0, min(1.0, score))
    finally:
        if close_db:
            db.close()


def get_best_agent(candidates: List[str]) -> Optional[str]:
    """
    Select the best agent from a list of candidates.

    Args:
        candidates: List of agent names to choose from

    Returns:
        Best agent name or None if no candidates
    """
    if not candidates:
        return None

    with SessionLocal() as db:
        scored = []
        for agent_name in candidates:
            score = calculate_score(agent_name, db)
            scored.append((score, agent_name))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None


def record_agent_performance(
    agent_name: str,
    success: bool,
    duration_ms: float,
    user_id: Optional[str] = None
) -> None:
    """
    Record agent performance for market ranking.

    Args:
        agent_name: Name of the agent
        success: Whether the agent succeeded
        duration_ms: Execution duration in milliseconds
        user_id: Optional user ID for stake rewards
    """
    with SessionLocal() as db:
        # Get or create ranking
        ranking = db.query(AgentRanking).filter_by(agent_name=agent_name).first()
        if not ranking:
            ranking = AgentRanking(agent_name=agent_name)
            db.add(ranking)

        # Update statistics
        if success:
            # Update success rate (moving average)
            ranking.success_rate = (ranking.success_rate * 0.9) + (1.0 * 0.1)
            ranking.avg_speed_ms = (ranking.avg_speed_ms * 0.9) + (duration_ms * 0.1)
        else:
            # Update failure rate
            ranking.failure_rate = (ranking.failure_rate * 0.9) + (1.0 * 0.1)

        ranking.last_updated = func.now()

        # Reward stakeholders if successful
        if success and user_id:
            # Find all stakeholders for this agent
            stakes = db.query(AgentStake).filter_by(agent_name=agent_name).all()
            for stake in stakes:
                # Small reward proportional to stake
                reward = 0.001 * stake.amount
                stake.amount += reward

        db.commit()

    # Emit performance event
    emit_agent_performance(agent_name, success, duration_ms)


def add_stake(user_id: str, agent_name: str, amount: float) -> bool:
    """
    Add stake to an agent.

    Args:
        user_id: User UUID as string
        agent_name: Name of the agent
        amount: Amount to stake

    Returns:
        True if successful, False otherwise
    """
    if amount <= 0:
        return False

    with SessionLocal() as db:
        # Get or create stake entry
        stake = db.query(AgentStake).filter_by(
            user_id=user_id,
            agent_name=agent_name
        ).first()

        if stake:
            stake.amount += amount
            stake.updated_at = time.time()
        else:
            stake = AgentStake(
                user_id=user_id,
                agent_name=agent_name,
                amount=amount
            )
            db.add(stake)

        # Update agent total stake
        ranking = db.query(AgentRanking).filter_by(agent_name=agent_name).first()
        if not ranking:
            ranking = AgentRanking(agent_name=agent_name)
            db.add(ranking)

        ranking.stake += amount
        db.commit()
        return True


def remove_stake(user_id: str, agent_name: str, amount: float) -> bool:
    """
    Remove stake from an agent.

    Args:
        user_id: User UUID as string
        agent_name: Name of the agent
        amount: Amount to remove

    Returns:
        True if successful, False otherwise
    """
    if amount <= 0:
        return False

    with SessionLocal() as db:
        stake = db.query(AgentStake).filter_by(
            user_id=user_id,
            agent_name=agent_name
        ).first()

        if not stake or stake.amount < amount:
            return False

        stake.amount -= amount
        if stake.amount == 0:
            db.delete(stake)

        # Update agent total stake
        ranking = db.query(AgentRanking).filter_by(agent_name=agent_name).first()
        if ranking:
            ranking.stake = max(0, ranking.stake - amount)

        db.commit()
        return True


def get_user_stakes(user_id: str) -> Dict[str, float]:
    """
    Get all stakes for a user.

    Args:
        user_id: User UUID as string

    Returns:
        Dictionary mapping agent names to stake amounts
    """
    with SessionLocal() as db:
        stakes = db.query(AgentStake).filter_by(user_id=user_id).all()
        return {stake.agent_name: stake.amount for stake in stakes}


def get_agent_rankings(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get top agent rankings.

    Args:
        limit: Maximum number of rankings to return

    Returns:
        List of ranking dictionaries
    """
    with SessionLocal() as db:
        rankings = db.query(AgentRanking).order_by(
            AgentRanking.stake.desc(),
            AgentRanking.success_rate.desc()
        ).limit(limit).all()

        result = []
        for ranking in rankings:
            score = calculate_score(ranking.agent_name, db)
            result.append({
                "agent_name": ranking.agent_name,
                "success_rate": ranking.success_rate,
                "failure_rate": ranking.failure_rate,
                "avg_speed_ms": ranking.avg_speed_ms,
                "stake": ranking.stake,
                "score": score,
                "last_updated": ranking.last_updated.isoformat() if ranking.last_updated else None
            })

        return result


def reset_agent_stats(agent_name: str) -> bool:
    """
    Reset agent statistics (admin function).

    Args:
        agent_name: Name of the agent

    Returns:
        True if successful, False if agent not found
    """
    with SessionLocal() as db:
        ranking = db.query(AgentRanking).filter_by(agent_name=agent_name).first()
        if not ranking:
            return False

        ranking.success_rate = 0.5
        ranking.failure_rate = 0.0
        ranking.avg_speed_ms = 100.0
        ranking.last_updated = func.now()
        db.commit()
        return True