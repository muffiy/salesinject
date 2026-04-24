"""
Celery task definitions for SalesInject.

Phase 3 – run_agent_task: calls OpenClaw with RAG-enriched prompt.
Phase 5 – scrape_ads_task (periodic beat), agent_learning_task.
"""
import httpx
from datetime import datetime, timezone
from celery import shared_task

from .worker import celery_app
from .core.config import settings


# ── Phase 3 ── Agent task (Celery) ────────────────────────────────────────────

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def run_agent_task(self, user_id: str, payload: dict) -> dict:
    """
    RAG-enriched ad generation via OpenClaw.
    payload keys: niche, product_name, agent_id, memories, ad_examples.
    Phase 5 populates memories & ad_examples before dispatching.
    """
    from .services.embedding_service import embed
    from .database import SessionLocal
    from .models import AgentMemory, Ad
    from sqlalchemy import text

    niche = payload.get("niche", "")
    product_name = payload.get("product_name", "")
    agent_id = payload.get("agent_id")
    action_type = payload.get("action_type", "ad_gen")
    memories: list = payload.get("memories", [])
    ad_examples: list = payload.get("ad_examples", [])

    if action_type == "scout":
        from .services.paperclip_agent import run_scout_mission
        from .database import SessionLocal

        location = payload.get("location", "Tunisia")
        chat_id = payload.get("chat_id")   # optional — set by bot handler

        db = SessionLocal()
        try:
            result = run_scout_mission(
                user_id=user_id,
                niche=niche,
                location=location,
                chat_id=chat_id,
                db=db,
            )
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": "Scout mission failed.",
                "error_detail": str(e),
            }
        finally:
            db.close()

        return result


    # ── RAG: fetch top-3 agent memories ──────────────────────────────────────
    if agent_id and not memories:
        try:
            query_embedding = embed(f"{niche} {product_name}")
            db = SessionLocal()
            try:
                rows = db.execute(
                    text("""
                        SELECT content FROM agent_memories
                        WHERE agent_id = :agent_id
                        ORDER BY embedding <=> CAST(:emb AS vector)
                        LIMIT 3
                    """),
                    {"agent_id": agent_id, "emb": str(query_embedding)},
                ).fetchall()
                memories = [r[0] for r in rows]
            finally:
                db.close()
        except Exception:
            pass  # RAG is best-effort — degrade gracefully

    # ── RAG: fetch top-3 similar ads ─────────────────────────────────────────
    if not ad_examples:
        try:
            if not memories:  # avoid re-embedding
                query_embedding = embed(f"{niche} {product_name}")
            db = SessionLocal()
            try:
                rows = db.execute(
                    text("""
                        SELECT creative_text FROM ads
                        WHERE niche = :niche
                        ORDER BY embedding <=> CAST(:emb AS vector)
                        LIMIT 3
                    """),
                    {"niche": niche, "emb": str(query_embedding)},
                ).fetchall()
                ad_examples = [r[0] for r in rows]
            finally:
                db.close()
        except Exception:
            pass

    # ── Build enriched prompt ─────────────────────────────────────────────────
    prompt = (
        f"You are an expert UGC ad copywriter. "
        f"Generate a compelling ad idea for the product: '{product_name}' "
        f"in the '{niche}' niche.\n"
    )
    if memories:
        prompt += "\n## Past successful content by this agent:\n" + "\n".join(f"- {m}" for m in memories)
    if ad_examples:
        prompt += "\n## Similar top-performing ads:\n" + "\n".join(f"- {a}" for a in ad_examples)
    prompt += "\n\nReturn JSON with keys: hook, format, angle, caption."

    # ── Call OpenClaw ─────────────────────────────────────────────────────────
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{settings.OPENCLAW_URL}/generate",
                json={"prompt": prompt, "user_id": user_id},
            )
            resp.raise_for_status()
            result = resp.json()
    except httpx.HTTPStatusError as exc:
        raise self.retry(exc=exc)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise self.retry(exc=exc)

    return {
        "status": "success",
        "ad_idea": result.get("ad_idea") or result,
    }


# ── Phase 5 ── Ad scraping beat task ──────────────────────────────────────────

NICHES_TO_SCRAPE = ["Fitness", "Beauty", "Finance", "Tech", "Food"]


@celery_app.task
def scrape_ads_task():
    """
    Periodic beat task: search Exa for ads in each niche, embed them,
    and upsert into the `ads` table. Runs daily via Celery Beat.
    """
    from .services.exa_service import search_ads
    from .services.embedding_service import embed
    from .database import SessionLocal
    from .models import Ad
    from sqlalchemy.dialects.postgresql import insert

    db = SessionLocal()
    try:
        for niche in NICHES_TO_SCRAPE:
            raw_ads = search_ads(niche, limit=10)
            for ad in raw_ads:
                if not ad.get("url") or not ad.get("text"):
                    continue
                creative_text = ad["text"][:2000]
                embedding = embed(creative_text)
                stmt = insert(Ad).values(
                    source="exa",
                    ad_url=ad["url"],
                    niche=niche,
                    creative_text=creative_text,
                    hooks=[],
                    engagement_data={},
                    embedding=embedding,
                    scraped_at=datetime.now(timezone.utc),
                ).on_conflict_do_update(
                    index_elements=["ad_url"],
                    set_={
                        "creative_text": creative_text,
                        "embedding": embedding,
                        "scraped_at": datetime.now(timezone.utc),
                    },
                )
                db.execute(stmt)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


# Configure periodic schedule on the celery app
celery_app.conf.beat_schedule = {
    "scrape-ads-daily": {
        "task": "app.tasks.scrape_ads_task",
        "schedule": 86400.0,  # Once every 24 hours
    },
}


# ── Phase 5 ── Agent learning task ────────────────────────────────────────────

@celery_app.task
def agent_learning_task(agent_id: str, task_id: str, submission_content: str):
    """
    Called when a UserTask submission is approved.
    - Embeds the submission content and inserts it into agent_memories.
    - Increments agent.tasks_completed and agent.total_earnings.
    - Called by the task approval endpoint (Phase 6).
    """
    from .services.embedding_service import embed
    from .database import SessionLocal
    from .models import AgentMemory, Agent, UserTask
    import uuid

    db = SessionLocal()
    try:
        # Fetch earnings from the user_task row
        ut = db.query(UserTask).filter(UserTask.id == task_id).first()
        earnings = float(ut.earnings or 0) if ut else 0.0

        # Store successful generation as a memory
        embedding = embed(submission_content)
        memory = AgentMemory(
            agent_id=agent_id,
            memory_type="successful_generation",
            content=submission_content[:1000],
            embedding=embedding,
            memory_metadata={"task_id": str(task_id), "earnings": earnings},
        )
        db.add(memory)

        # Update agent stats
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            agent.tasks_completed = (agent.tasks_completed or 0) + 1
            agent.total_earnings = float(agent.total_earnings or 0) + earnings

        db.commit()
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()
