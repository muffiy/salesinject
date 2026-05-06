"""
AI Provider Router

Minimal, production-friendly abstraction around LLM providers.

Current implementation:
- OpenRouter (Chat Completions) via `OPENROUTER_API_KEY`
- Mock fallback when no key is configured

Returns a normalized response:
{
  "content": "<string>",
  "usage": {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int} | {}
}
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from app.core.config_v2 import settings


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class AIProviderRouter:
    async def generate(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        if settings.OPENROUTER_API_KEY:
            return await self._openrouter_chat(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout_seconds=timeout_seconds or settings.DEFAULT_GENERATION_TIMEOUT,
            )

        return self._mock_response(system_prompt=system_prompt, user_prompt=user_prompt)

    async def _openrouter_chat(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.MINI_APP_URL:
            headers["HTTP-Referer"] = settings.MINI_APP_URL
            headers["X-Title"] = "SalesInject"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=float(timeout_seconds)) as client:
            resp = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        usage = data.get("usage") or {}
        return {"content": content, "usage": usage, "provider": "openrouter", "model": model}

    def _mock_response(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        # Keep output as JSON to match the content service parser expectations.
        content = (
            '{\n'
            f'  "text": "[MOCK] {user_prompt[:200].replace(chr(34), chr(39))}",\n'
            '  "headline": "",\n'
            '  "hashtags": [],\n'
            '  "cta": "",\n'
            '  "meta": {"word_count": 0, "estimated_read_time": "0 min", "sentiment": "neutral"}\n'
            '}\n'
        )
        return {"content": content, "usage": {}, "provider": "mock", "model": "mock"}

