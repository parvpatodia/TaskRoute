from typing import Any, Dict, Optional

from catalog import load_items
from decision import rank_candidates
from market import apply_market_to_price


def compute_effective_price(candidate: Dict[str, Any], tokens_used: int) -> float:
    base_price = float(candidate.get("price", 999999.0))
    unit = str(candidate.get("price_unit", ""))

    if unit == "per_1k_tokens_usd":
        base_price = base_price * (tokens_used / 1000.0)

    provider = str(candidate.get("provider"))
    return apply_market_to_price(provider, base_price)


def recommend_plan(
    task_type: str,
    budget_usd: float,
    objective: str,
    current_provider: Optional[str],
    state_tokens: int,
) -> Dict[str, Any]:

    items = load_items()
    candidates = [it for it in items if task_type in it.get("task_types", [])]

    if not candidates:
        return {"ok": False, "error": "No candidates found", "task_type": task_type}

    tokens_used = 1200 if task_type == "text_generation" else 0

    enriched = []
    for c in candidates:
        c2 = dict(c)
        c2["effective_price"] = compute_effective_price(c2, tokens_used)
        enriched.append(c2)

    feasible = [c for c in enriched if float(c.get("effective_price", 999999.0)) <= budget_usd]
    pool = feasible if feasible else enriched

    ranked = rank_candidates(
        candidates=pool,
        objective=objective,
        current_provider=current_provider,
        state_tokens=state_tokens,
        validation_calls=1,
        validation_call_cost_usd=0.0005,
        risk_weight_usd=0.01
    )

    best = ranked[0]

    note = None
    if not feasible:
        note = "No option fits the budget at current market prices. Returning best available."

    return {
        "ok": True,
        "task_type": task_type,
        "budget_usd": budget_usd,
        "objective": objective,
        "note": note,
        "recommendation": best,
        "top_options": ranked[:5]
    }