def calculate_payout(claim_id: str, is_winner: bool, ai_score: float) -> float:
    _ = claim_id
    base = 15.0
    multiplier = 1.0 if is_winner else 0.5
    quality = max(0.5, min(ai_score, 1.2))
    return round(base * multiplier * quality, 2)
