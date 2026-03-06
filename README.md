# TaskRoute

TaskRoute is a small service that picks a provider and model for a given task under a budget. You send `task_type`, `budget_usd`, and `objective`; it returns a recommendation plus a score breakdown (base score, switching cost, risk penalty).

## How it works

- **Catalog** (`catalog.py`) loads candidate models from `providers.json`. Each item has `provider`, `name`, `task_types`, `price`, `price_unit`, `latency`, `quality`, `reliability`.
- **Planner** (`planner.py`) filters by `task_type`, computes `effective_price` via `market.apply_market_to_price` (base price × provider multiplier), drops anything over budget into a “best available” fallback, then calls `decision.rank_candidates`.
- **Decision** (`decision.py`) scores each candidate: `base_objective_score` (cost / speed / quality / balanced), minus `switching_cost_usd` (migration + validation if you change provider) and `risk_penalty_usd` (from reliability). Sorts by `total_score` and returns the ranked list with a `breakdown` per option.
- **Market** (`market.py`, `market_state.py`) keeps `provider_multipliers` in `data/market_state.json`. `apply_market_to_price` multiplies catalog price by the current multiplier. You can jitter or shock the market (e.g. bump openai, drop replicate) with `market_controller.py` or from the agent economy run.

So: catalog → feasible set by budget → rank by objective + switching cost + risk → one recommendation.

## API

- **GET /**  
  Health: `{"ok": true, "service": "taskroute"}`.

- **POST /optimize**  
  Body: `task_type`, `budget_usd`, `objective` (cost | speed | quality | balanced), optional `current_provider`, optional `state_tokens` (default 1200).  
  Response: `ok`, `recommendation` (provider, name, effective_price, breakdown), `top_options`, and optional `note` if nothing was feasible.

CORS is open for local/frontend use.

## Running it

```bash
# venv
source activate/bin/activate   # or .venv/bin/activate
pip install -r requirements.txt

# server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then hit `http://127.0.0.1:8000/optimize` with a JSON body.

## Scripts

- **`agent_economy.py`** – Simulates an autonomous agent economy: multiple agents (CreativeAI, DocuMind, DataForge) with fixed `task`, `budget`, `revenue_per_job`, `state_tokens`. Each step picks an agent, loads market state, optionally jitters or applies shocks (e.g. openai +40%, replicate -25%), POSTs to `/optimize` with the chosen objective (cost/speed/quality/balanced). Uses the recommendation’s `effective_price` vs revenue to decide if the job runs or is skipped; tracks `current_provider` and prints switching cost / risk penalty when the agent flips providers. Good for seeing how recommendations change under market moves and budget constraints.
- **`buyer_agent.py`** – Single buyer agent: picks a task type, decides priority (e.g. quality for image_generation, cost for text_generation), calls `/optimize`, and spends budget on the returned recommendation. Tracks remaining budget and provider usage.
- **`market_controller.py`** – CLI to load/save `market_state.json`: jitter multipliers, apply a shock to a provider (e.g. openai 1.4x), or reset all to 1.0.

## Jargon quick ref

| Term | Meaning |
|------|--------|
| `task_type` | e.g. `image_generation`, `text_generation`, `data_processing` |
| `effective_price` | Catalog price × `provider_multipliers[provider]` |
| `state_tokens` | Used for switching cost when migrating (e.g. re-prompting); scales migration cost in `decision.switching_cost_usd` |
| `provider_multipliers` | Per-provider factor in `data/market_state.json`; 1.0 = catalog price |
| `base_score` | Score from objective only (e.g. −price for cost, latency for speed) |
| `switching_cost_usd` | Migration (tokens × unit price) + validation calls × cost; penalized in total score |
| `risk_penalty_usd` | `(1 - reliability) × risk_weight_usd`; also penalized in total score |
| `feasible` | Candidates with `effective_price <= budget_usd`; if none, planner still returns best available and sets `note` |

## Repo layout

- `main.py` – FastAPI app, `/` and `/optimize`; calls `planner.recommend_plan`.
- `planner.py` – Load catalog, filter by task, apply market to price, feasibility filter, rank, return recommendation + top_options.
- `decision.py` – `rank_candidates`, `switching_cost_usd`, `risk_penalty_usd`, `base_objective_score`.
- `catalog.py` – `load_items()` from `providers.json`.
- `market.py` – `apply_market_to_price(provider, base_price)`.
- `market_state.py` – load/save/reset/jitter/shock `data/market_state.json`.
- `market_controller.py` – CLI for market state.
- `agent_economy.py` – Multi-agent sim calling `/optimize`; market shocks and budgets.
- `buyer_agent.py` – Single-agent buyer script.
- `llm_explain.py` – Stub for explaining a recommendation (breakdown text); can be wired to an LLM later.
