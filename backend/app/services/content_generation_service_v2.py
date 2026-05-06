"""
Content Generation Service v2

Supports:
- Multi-format content generation (social, blog, email, ad, script)
- Brand voice injection with guidelines
- Template-based generation
- Variant generation for A/B testing
- Content repurposing across platforms
- Rate limiting + caching (Redis v2)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config_v2 import settings
from app.core.redis_v2 import redis_manager
from app.models.content import BrandVoice, ContentPiece, ContentTemplate
from app.services.ai_providers import AIProviderRouter


class RateLimitExceeded(Exception):
    pass


class ContentGenerationService:
    def __init__(self) -> None:
        self.ai_router = AIProviderRouter()
        self.cache_ttl = 3600  # 1 hour

    async def generate(
        self,
        *,
        db: AsyncSession,
        user_id: str,
        prompt: str,
        content_type: str = "social_post",
        brand_voice_id: Optional[str] = None,
        template_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        tone: str = "professional",
        language: str = "en",
        max_length: Optional[int] = None,
        model_tier: str = "tier_2",
    ) -> dict[str, Any]:
        # 1) Rate limiting
        allowed, remaining = await redis_manager.rate_limit_check(
            f"gen:{user_id}",
            max_requests=settings.MAX_GENERATIONS_PER_HOUR,
            window=3600,
        )
        if not allowed:
            raise RateLimitExceeded("Hourly generation limit reached")

        # 2) Cache check (dedup)
        cache_key = self._generate_cache_key(prompt, content_type, brand_voice_id, template_id, tone, language, model_tier)
        cached = await redis_manager.cache_get(cache_key)
        if cached:
            return {**cached, "cached": True, "remaining": remaining}

        user_uuid = uuid.UUID(user_id)

        # 3) Load brand voice
        brand_voice: BrandVoice | None = None
        if brand_voice_id:
            result = await db.execute(
                select(BrandVoice).where(BrandVoice.id == uuid.UUID(brand_voice_id), BrandVoice.user_id == user_uuid),
            )
            brand_voice = result.scalar_one_or_none()

        # 4) Load template
        template: ContentTemplate | None = None
        if template_id:
            result = await db.execute(
                select(ContentTemplate).where(ContentTemplate.id == uuid.UUID(template_id), ContentTemplate.user_id == user_uuid),
            )
            template = result.scalar_one_or_none()

        # 5) Build system prompt
        system_prompt = self._build_system_prompt(
            content_type=content_type,
            brand_voice=brand_voice,
            template=template,
            tone=tone,
            language=language,
            max_length=max_length or settings.MAX_CONTENT_LENGTH,
        )

        # 6) Call AI provider
        model = self._get_model_for_tier(model_tier)
        temperature = 0.8 if tone in ("witty", "casual", "creative") else 0.4
        response = await self.ai_router.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=prompt,
            max_tokens=max_length or settings.MAX_CONTENT_LENGTH,
            temperature=temperature,
        )

        # 7) Parse output
        parsed_content = self._parse_ai_output(response, content_type)

        # 8) Store in database
        content_piece = ContentPiece(
            user_id=user_uuid,
            content_type=content_type,
            prompt=prompt,
            raw_output=response,
            parsed_content=parsed_content,
            brand_voice_id=uuid.UUID(brand_voice_id) if brand_voice_id else None,
            template_id=uuid.UUID(template_id) if template_id else None,
            model_used=model,
            tokens_used=int((response.get("usage") or {}).get("total_tokens") or 0),
            metadata={
                "tone": tone,
                "language": language,
                "context": context or {},
            },
        )
        db.add(content_piece)
        await db.commit()
        await db.refresh(content_piece)

        # 9) Cache result
        result = {
            "id": str(content_piece.id),
            "content": parsed_content,
            "content_type": content_type,
            "model": model,
            "tokens_used": content_piece.tokens_used,
            "created_at": content_piece.created_at.isoformat() if content_piece.created_at else None,
            "remaining": max(0, remaining - 1),
        }
        await redis_manager.cache_set(cache_key, result, ttl=self.cache_ttl)
        return result

    async def generate_variants(
        self,
        *,
        db: AsyncSession,
        user_id: str,
        base_content_id: str,
        variant_count: int = 3,
        variation_axes: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        result = await db.execute(
            select(ContentPiece).where(ContentPiece.id == uuid.UUID(base_content_id), ContentPiece.user_id == uuid.UUID(user_id)),
        )
        base = result.scalar_one_or_none()
        if not base:
            raise ValueError("Base content not found")

        axes = variation_axes or ["tone", "hook"]
        variants: list[dict[str, Any]] = []

        base_text = (base.parsed_content or {}).get("text") or ""
        for i in range(variant_count):
            axis = axes[i % len(axes)]
            variant_prompt = (
                f"Original content:\n{base_text}\n\n"
                f"Create a variant that changes the {axis} while keeping the core message.\n"
                "Make it distinctly different but equally effective."
            )

            variant = await self.generate(
                db=db,
                user_id=user_id,
                prompt=variant_prompt,
                content_type=base.content_type,
                brand_voice_id=str(base.brand_voice_id) if base.brand_voice_id else None,
                template_id=str(base.template_id) if base.template_id else None,
                tone="creative",
                model_tier="tier_1",
            )
            variant["variant_of"] = base_content_id
            variant["variation_axis"] = axis
            variants.append(variant)

        return variants

    async def repurpose(
        self,
        *,
        db: AsyncSession,
        user_id: str,
        content_id: str,
        target_formats: list[str],
    ) -> dict[str, Any]:
        result = await db.execute(
            select(ContentPiece).where(ContentPiece.id == uuid.UUID(content_id), ContentPiece.user_id == uuid.UUID(user_id)),
        )
        original = result.scalar_one_or_none()
        if not original:
            raise ValueError("Content not found")

        original_text = (original.parsed_content or {}).get("text") or ""

        repurposed: dict[str, Any] = {}
        for fmt in target_formats:
            prompt = (
                f"Repurpose this content for {fmt}:\n\n"
                f"Original:\n{original_text}\n\n"
                f"Requirements for {fmt}:\n{self._get_format_requirements(fmt)}"
            )
            repurposed[fmt] = await self.generate(
                db=db,
                user_id=user_id,
                prompt=prompt,
                content_type=fmt,
                brand_voice_id=str(original.brand_voice_id) if original.brand_voice_id else None,
                template_id=str(original.template_id) if original.template_id else None,
                model_tier="tier_2",
            )

        return {"original_id": content_id, "repurposed": repurposed}

    def _generate_cache_key(self, *args: Any) -> str:
        key_string = "|".join("" if a is None else str(a) for a in args)
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()[:32]

    def _get_model_for_tier(self, tier: str) -> str:
        tiers = {
            "tier_1": settings.CONTENT_MODEL_TIER_1,
            "tier_2": settings.CONTENT_MODEL_TIER_2,
            "tier_3": settings.CONTENT_MODEL_TIER_3,
        }
        return tiers.get(tier, settings.CONTENT_MODEL_TIER_2)

    def _build_system_prompt(
        self,
        *,
        content_type: str,
        brand_voice: Optional[BrandVoice],
        template: Optional[ContentTemplate],
        tone: str,
        language: str,
        max_length: int,
    ) -> str:
        parts: list[str] = [
            f"You are an expert content creator specializing in {content_type}.",
            f"Language: {language}",
            f"Tone: {tone}",
            f"Maximum length: {max_length} characters",
        ]

        if brand_voice:
            parts.append(
                "\n".join(
                    [
                        "BRAND VOICE GUIDELINES:",
                        f"- Personality: {brand_voice.personality or ''}",
                        f"- Writing style: {brand_voice.writing_style or ''}",
                        f"- Forbidden words: {', '.join(brand_voice.forbidden_words or [])}",
                        f"- Preferred phrases: {', '.join(brand_voice.preferred_phrases or [])}",
                        f"- Emoji usage: {brand_voice.emoji_style or ''}",
                    ]
                )
            )

        if template:
            parts.append(
                "\n".join(
                    [
                        "TEMPLATE STRUCTURE:",
                        template.structure or "",
                        "",
                        f"Variables to fill: {', '.join(template.variables or [])}",
                    ]
                )
            )

        parts.append(
            "\n".join(
                [
                    "OUTPUT FORMAT (JSON):",
                    "{",
                    '  "text": "the generated content",',
                    '  "headline": "optional headline",',
                    '  "hashtags": ["tag1", "tag2"],',
                    '  "cta": "call to action",',
                    '  "meta": {',
                    '    "word_count": 0,',
                    '    "estimated_read_time": "0 min",',
                    '    "sentiment": "positive/neutral/negative"',
                    "  }",
                    "}",
                ]
            )
        )

        return "\n\n".join(parts)

    def _parse_ai_output(self, response: dict[str, Any], content_type: str) -> dict[str, Any]:
        content = response.get("content", "") or ""
        try:
            # Strip markdown fences if present
            if "```json" in content:
                content = content.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in content:
                content = content.split("```", 1)[1].split("```", 1)[0]

            parsed = json.loads(content.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        raw_text = response.get("content", "") or ""
        return {
            "text": raw_text,
            "headline": "",
            "hashtags": [],
            "cta": "",
            "meta": {"word_count": len(raw_text.split())},
        }

    def _get_format_requirements(self, fmt: str) -> str:
        requirements = {
            "twitter": "- Max 280 chars\n- Use 2-3 hashtags\n- Strong hook in first 50 chars",
            "linkedin": "- Professional tone\n- 3-5 paragraphs\n- Use bullet points\n- Include CTA",
            "instagram": "- Casual, visual tone\n- Use emojis\n- 5-10 hashtags\n- Include question for engagement",
            "email": "- Subject line + body\n- Personalization tokens\n- Clear CTA button text\n- Preview text",
        }
        return requirements.get(fmt, "- Adapt to platform best practices")


content_generation_service = ContentGenerationService()

