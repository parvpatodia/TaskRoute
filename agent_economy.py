import requests
import random
import time

from market_state import load_market_state, save_market_state, reset_market, jitter_market, apply_shock


TASKROUTE_URL = "http://127.0.0.1:8000/optimize"


def choose_objective():
    print()
    print("Choose objective")
    print("1 cost")
    print("2 speed")
    print("3 quality")
    print("4 balanced")
    print()

    choice = input("Objective: ").strip()

    mapping = {
        "1": "cost",
        "2": "speed",
        "3": "quality",
        "4": "balanced"
    }

    return mapping.get(choice, "balanced")


agents = [
    {
        "name": "CreativeAI",
        "task": "image_generation",
        "budget": 0.10,
        "revenue_per_job": 0.03,
        "state_tokens": 1800,
        "current_provider": None
    },
    {
        "name": "DocuMind",
        "task": "text_generation",
        "budget": 0.10,
        "revenue_per_job": 0.002,
        "state_tokens": 2200,
        "current_provider": None
    },
    {
        "name": "DataForge",
        "task": "data_processing",
        "budget": 0.10,
        "revenue_per_job": 0.006,
        "state_tokens": 900,
        "current_provider": None
    }
]


def print_market_snapshot():
    state = load_market_state()
    multipliers = state.get("provider_multipliers", {})
    parts = []
    for k in ["openai", "replicate", "aws", "databricks"]:
        if k in multipliers:
            parts.append(f"{k} {multipliers[k]}")
    print("Market:", " | ".join(parts))


def run_economy():
    objective = choose_objective()

    reset_market()

    print()
    print("===== Autonomous Agent Economy =====")
    print("Objective:", objective)
    print_market_snapshot()
    print()

    for step in range(15):
        state = load_market_state()
        state = jitter_market(state, jitter=0.02)

        if step == 5:
            state = apply_shock(state, "openai", 1.4)
            print("Market event: OpenAI prices increased")
        if step == 9:
            state = apply_shock(state, "replicate", 0.75)
            print("Market event: Replicate prices dropped")

        save_market_state(state)

        agent = random.choice(agents)

        print("Step:", step + 1)
        print("Agent:", agent["name"])
        print("Task:", agent["task"])
        print("Budget:", round(agent["budget"], 6))
        print_market_snapshot()

        payload = {
            "task_type": agent["task"],
            "budget_usd": agent["budget"],
            "objective": objective,
            "current_provider": agent["current_provider"],
            "state_tokens": agent["state_tokens"]
        }

        response = requests.post(TASKROUTE_URL, json=payload)
        data = response.json()

        if not data.get("ok"):
            print("Planner error:", data.get("error"))
            print()
            time.sleep(1.2)
            continue

        rec = data["recommendation"]
        provider = rec["provider"]
        model = rec["name"]
        cost = float(rec["effective_price"])

        revenue = agent["revenue_per_job"]
        profit = revenue - cost

        if profit < 0 and objective in ["cost", "balanced"]:
            print("Agent decision: skipped job due to negative profit")
            print("Chosen provider:", provider)
            print("Model:", model)
            print("Estimated cost:", round(cost, 6))
            print("Revenue:", revenue)
            print("Estimated profit:", round(profit, 6))
            print("------------------------------------")
            print()
            time.sleep(1.2)
            continue

        if cost > agent["budget"]:
            print("Agent decision: cannot afford job")
            print("Chosen provider:", provider)
            print("Model:", model)
            print("Estimated cost:", round(cost, 6))
            print("------------------------------------")
            print()
            time.sleep(1.2)
            continue

        previous_provider = agent["current_provider"]
        switched = previous_provider is not None and previous_provider != provider

        agent["budget"] = agent["budget"] - cost + revenue
        agent["current_provider"] = provider

        breakdown = rec.get("breakdown", {})

        print("Chosen provider:", provider)
        print("Model:", model)
        print("Estimated cost:", round(cost, 6))
        print("Revenue:", revenue)
        print("Profit:", round(profit, 6))
        print("New budget:", round(agent["budget"], 6))

        if switched:
            print("Provider switched from", previous_provider, "to", provider)
            print("Switching cost estimate:", breakdown.get("switching_cost_usd"))
            print("Risk penalty:", breakdown.get("risk_penalty_usd"))

        print("Planner reasoning")
        print("Base score:", breakdown.get("base_score"))
        print("Total score:", breakdown.get("total_score"))
        print("------------------------------------")
        print()

        time.sleep(1.2)


if __name__ == "__main__":
    run_economy()