"""
Paperclip Agent — Scout Mission Orchestrator

run_scout_mission() chains the five paperclip tools sequentially,
manages the shared DB session, and emits a Telegram completion
notification. This is the single entry point called by the Celery task.
"""

from typing import Optional
from sqlalchemy.orm import Session


def run_scout_mission(
    user_id: str,
    niche: str,
    location: str,
    chat_id: Optional[int],
    db: Session,
) -> dict:
    """
    Chain scout tools sequentially for one complete mission.

    Step 1: Find influencers  (Exa neural search)
    Step 2: Analyze & rank    (Agent Zero stub — deterministic)
    Step 3: Save scout report (scout_reports table, map data for DeckGL)
    Step 4: Save paperclip    (paperclip_items: mission_log + profiles + ad_copy)
    Step 5: Notify user       (Telegram message — fails silently)

    The `db` session is provided by the Celery task so all
    flush/commit cycles remain in one transaction context.

    Returns:
        {
            "status": "success" | "error",
            "influencer_count": int,
            "report": str,
            "scout_record_id": str,
            "paperclip_rows": int,
            "telegram": {"status": "sent" | "failed"},
        }
    """
    from ..tools.paperclip_tools import (
        scout_influencers,
        analyze_and_rank,
        save_scout_report,
        save_scout_results,
        notify_telegram,
    )

    # ── Step 1: Scout influencers ──────────────────────────────────────────
    influencers = scout_influencers(niche=niche, location=location)

    # ── Step 2: Agent Zero analysis ────────────────────────────────────────
    report = analyze_and_rank(influencers_data=influencers, niche=niche)

    # ── Step 3: Persist to scout_reports (map data for frontend) ──────────
    scout_result = save_scout_report(
        user_id=user_id,
        influencers=influencers,
        niche=niche,
        db=db,
    )

    # ── Step 4: Persist Paperclip items (mission_log, profiles, ad draft) ──
    ad_copy_draft = f"🎯 New {niche} campaign — {len(influencers)} influencers scouted in {location}."
    paperclip_result = save_scout_results(
        user_id=user_id,
        task_id=None,          # No UserTask foreign key for scout missions
        influencers=influencers,
        report=report,
        ad_copy=ad_copy_draft,
        db=db,
    )

    # ── Step 5: Telegram notification (non-blocking) ───────────────────────
    telegram_status = {"status": "skipped"}
    if chat_id:
        top_line = report.split("\n")[0] if report else "Scout complete."
        notification_text = (
            f"📡 *Scout Mission Complete*\n\n"
            f"{top_line}\n\n"
            f"{len(influencers)} targets identified in *{location}*."
        )
        telegram_status = notify_telegram(chat_id=chat_id, message=notification_text)

    # ── Commit all flushed writes in one shot ──────────────────────────────
    db.commit()

    return {
        "status": "success",
        "influencer_count": len(influencers),
        "report": report,
        "scout_record_id": scout_result.get("record_id"),
        "paperclip_rows": paperclip_result.get("rows_written", 0),
        "telegram": telegram_status,
    }
