from typing import List, Dict, Any
import json
from app.core.config import settings


def analyze_influencers(influencers_data: List[Dict[str, Any]], niche: str) -> str:
    """
    Analyzes and ranks an extracted list of influencer profiles using OpenAI.
    """
    if not influencers_data:
        return f"No targets found in the {niche} niche."

    if not settings.OPENAI_API_KEY:
        return "ERROR: OPENAI_API_KEY is not configured in the environment."

    # Pre-filter to reduce token size — top 10 by followers
    ranked = sorted(influencers_data, key=lambda x: x.get('followers', 0), reverse=True)[:10]

    prompt = f"""
    You are an expert Influencer Marketing Agent. I have a list of influencers in the '{niche}' niche.
    Please analyze these profiles and provide a concise, ranked report of the top 3 best fits for a brand campaign.
    For each of the top 3, explain WHY they are a good fit based on their metrics.

    Influencer Data:
    {json.dumps(ranked, indent=2)}
    """

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strategic influencer marketing assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or "No response from model."

    except Exception as e:
        return f"Failed to analyze influencers using OpenAI: {str(e)}"
