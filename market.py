from market_state import load_market_state


def apply_market_to_price(provider: str, base_price: float) -> float:
    state = load_market_state()
    multipliers = state.get("provider_multipliers", {})
    m = float(multipliers.get(provider, 1.0))
    return round(base_price * m, 6)