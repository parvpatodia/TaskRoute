import json
import os
import random
import time
from typing import Any, Dict

MARKET_PATH = os.path.join("data", "market_state.json")


def default_state() -> Dict[str, Any]:
    return {
        "updated_at": int(time.time()),
        "provider_multipliers": {
            "openai": 1.0,
            "replicate": 1.0,
            "aws": 1.0,
            "databricks": 1.0,
            "apify": 1.0,
            "requests": 1.0
        }
    }


def load_market_state() -> Dict[str, Any]:
    if not os.path.exists(MARKET_PATH):
        return default_state()
    with open(MARKET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_market_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(MARKET_PATH), exist_ok=True)
    state["updated_at"] = int(time.time())
    with open(MARKET_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def reset_market() -> Dict[str, Any]:
    state = default_state()
    save_market_state(state)
    return state


def jitter_market(state: Dict[str, Any], jitter: float = 0.03) -> Dict[str, Any]:
    multipliers = state.get("provider_multipliers", {})
    for p in list(multipliers.keys()):
        base = float(multipliers[p])
        change = random.uniform(1.0 - jitter, 1.0 + jitter)
        multipliers[p] = round(max(0.6, min(2.0, base * change)), 4)
    state["provider_multipliers"] = multipliers
    return state


def apply_shock(state: Dict[str, Any], provider: str, factor: float) -> Dict[str, Any]:
    multipliers = state.get("provider_multipliers", {})
    current = float(multipliers.get(provider, 1.0))
    multipliers[provider] = round(max(0.6, min(3.0, current * factor)), 4)
    state["provider_multipliers"] = multipliers
    return state