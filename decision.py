from typing import Any, Dict, List, Optional


LATENCY_SCORE = {"fast": 3.0, "medium": 2.0, "slow": 1.0}


def switching_cost_usd(
    current_provider: Optional[str],
    candidate_provider: str,
    state_tokens: int,
    validation_calls: int,
    validation_call_cost_usd: float,
    price_unit: str,
    effective_unit_price: float
) -> float:

    if not current_provider:
        return 0.0

    if candidate_provider == current_provider:
        return 0.0

    migration = 0.0
    if price_unit == "per_1k_tokens_usd":
        migration = (state_tokens / 1000.0) * effective_unit_price

    validation = validation_calls * validation_call_cost_usd
    return migration + validation


def risk_penalty_usd(reliability: float, risk_weight_usd: float) -> float:
    failure_prob = max(0.0, 1.0 - reliability)
    return failure_prob * risk_weight_usd


def base_objective_score(objective: str, quality: float, latency: str, effective_price: float) -> float:
    latency_score = LATENCY_SCORE.get(latency, 2.0)

    if objective == "cost":
        return -effective_price

    if objective == "quality":
        return quality

    if objective == "speed":
        return latency_score

    if objective == "balanced":
        return (quality * 1.0) + (latency_score * 0.5) - (effective_price * 50.0)

    return -effective_price


def rank_candidates(
    candidates: List[Dict[str, Any]],
    objective: str,
    current_provider: Optional[str],
    state_tokens: int,
    validation_calls: int,
    validation_call_cost_usd: float,
    risk_weight_usd: float,
) -> List[Dict[str, Any]]:

    scored = []

    for c in candidates:
        provider = str(c.get("provider"))
        name = str(c.get("name"))
        price_unit = str(c.get("price_unit"))
        effective_price = float(c.get("effective_price"))
        quality = float(c.get("quality", 0.0))
        latency = str(c.get("latency", "medium"))
        reliability = float(c.get("reliability", 0.95))

        base = base_objective_score(objective, quality, latency, effective_price)

        sw_cost = switching_cost_usd(
            current_provider=current_provider,
            candidate_provider=provider,
            state_tokens=state_tokens,
            validation_calls=validation_calls,
            validation_call_cost_usd=validation_call_cost_usd,
            price_unit=price_unit,
            effective_unit_price=effective_price
        )

        risk = risk_penalty_usd(reliability, risk_weight_usd)

        total = base - (sw_cost * 30.0) - (risk * 30.0)

        scored.append((c, total, base, sw_cost, risk))

    scored.sort(key=lambda x: x[1], reverse=True)

    ranked = []
    for c, total, base, sw_cost, risk in scored:
        ranked.append({
            "provider": c.get("provider"),
            "name": c.get("name"),
            "price_unit": c.get("price_unit"),
            "effective_price": round(float(c.get("effective_price")), 6),
            "latency": c.get("latency"),
            "quality": c.get("quality"),
            "reliability": c.get("reliability"),
            "breakdown": {
                "objective": objective,
                "base_score": round(base, 6),
                "switching_cost_usd": round(sw_cost, 6),
                "risk_penalty_usd": round(risk, 6),
                "total_score": round(total, 6),
                "current_provider": current_provider
            }
        })

    return ranked