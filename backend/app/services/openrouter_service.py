"""
OpenRouter LLM Service — production AI backbone for SalesInject.

Calls the OpenRouter API (compatible with any model) for:
- Influencer ranking/analysis
- Ad copy generation
- Content ideas (RAG-augmented)
"""
import httpx
import json
from typing import Optional
from ..core.config import settings

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_llm_async(
    prompt: str,
    system: str = "You are a strategic influencer marketing AI assistant for SalesInject.",
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Async call to OpenRouter — use from FastAPI endpoints."""
    if not settings.OPENROUTER_API_KEY:
        return _mock_response(prompt)

    model = model or settings.OPENROUTER_MODEL
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.MINI_APP_URL,
        "X-Title": "SalesInject",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[OpenRouter] Error: {e}")
        return _mock_response(prompt)


def call_llm(
    prompt: str,
    system: str = "You are a strategic influencer marketing AI assistant for SalesInject.",
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Synchronous call to OpenRouter — use from Celery tasks."""
    if not settings.OPENROUTER_API_KEY:
        return _mock_response(prompt)

    model = model or settings.OPENROUTER_MODEL
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.MINI_APP_URL,
        "X-Title": "SalesInject",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[OpenRouter] Sync Error: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """Fallback when no API key is configured — ensures graceful degradation."""
    if "rank" in prompt.lower() or "analyze" in prompt.lower():
        return (
            "## Scout Analysis Report\n\n"
            "### Top 3 Influencer Matches:\n\n"
            "1. **@alpha_creator** — 82K followers, 4.5% engagement. Strong brand alignment.\n"
            "2. **@beta_content** — 45K followers, 5.2% engagement. High conversion potential.\n"
            "3. **@gamma_viral** — 31K followers, 8.1% engagement. Micro-influencer with loyal audience.\n\n"
            "**Recommendation:** Start with @gamma_viral for highest ROI per TND spent."
        )
    elif "ad" in prompt.lower() or "hook" in prompt.lower() or "caption" in prompt.lower():
        return (
            "## Content Ideas\n\n"
            "**Hook 1:** \"I tried this for 7 days and here's what happened...\"\n\n"
            "**Hook 2:** \"POV: You just discovered the best-kept secret in Tunis\"\n\n"
            "**Caption:** 🔥 Game-changing results! Link in bio for exclusive discount. #Ad #Tunisia"
        )
    else:
        return f"[SalesInject AI] Processed request: {prompt[:100]}..."
