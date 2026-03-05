import json
from pathlib import Path
from typing import Any, Dict, List


PROVIDERS_PATH = Path(__file__).parent / "providers.json"


def load_providers() -> Dict[str, List[Dict[str, Any]]]:
    with open(PROVIDERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def recommend_plan(task_type: str, budget_usd: float, priority: str) -> Dict[str, Any]:
    providers = load_providers()

    if task_type not in providers:
        return {
            "ok": False,
            "error": f"Unknown task_type: {task_type}. Supported: {list(providers.keys())}"
        }

    options = providers[task_type]

    def estimated_cost(option: Dict[str, Any]) -> float:
        if task_type == "text_generation":
            return option["cost_per_1k_tokens_usd"]
        if task_type == "image_generation":
            return option["cost_per_image_usd"]
        if task_type == "web_scraping":
            return option["cost_per_request_usd"]
        return 999.0

    feasible = []
    for opt in options:
        cost = estimated_cost(opt)
        if cost <= budget_usd:
            feasible.append((opt, cost))

    if not feasible:
        cheapest = min(options, key=lambda o: estimated_cost(o))
        return {
            "ok": True,
            "task_type": task_type,
            "priority": priority,
            "budget_usd": budget_usd,
            "recommendation": {
                "name": cheapest["name"],
                "provider": cheapest["provider"]
            },
            "estimated_cost_usd": estimated_cost(cheapest),
            "note": "No option fits the budget. Returning the cheapest available option."
        }

    if priority == "cost":
        best = min(feasible, key=lambda x: x[1])[0]
    elif priority == "quality":
        best = max(feasible, key=lambda x: x[0].get("quality", 0))[0]
    elif priority == "speed":
        speed_rank = {"fast": 3, "medium": 2, "slow": 1}
        best = max(feasible, key=lambda x: speed_rank.get(x[0].get("latency", "medium"), 2))[0]
    else:
        best = max(feasible, key=lambda x: x[0].get("quality", 0))[0]

    return {
        "ok": True,
        "task_type": task_type,
        "priority": priority,
        "budget_usd": budget_usd,
        "recommendation": {
            "name": best["name"],
            "provider": best["provider"]
        },
        "estimated_cost_usd": estimated_cost(best),
        "alternatives": [
            {
                "name": opt["name"],
                "provider": opt["provider"],
                "estimated_cost_usd": estimated_cost(opt),
                "latency": opt.get("latency"),
                "quality": opt.get("quality")
            }
            for opt in options
        ]
    }