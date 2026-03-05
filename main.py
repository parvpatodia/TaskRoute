from fastapi import FastAPI
from pydantic import BaseModel
from planner import recommend_plan


app = FastAPI(title="TaskRoute", version="0.1")


class OptimizeRequest(BaseModel):
    task_type: str
    budget_usd: float
    priority: str  # cost, quality, speed


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/optimize")
def optimize(req: OptimizeRequest):
    return recommend_plan(req.task_type, req.budget_usd, req.priority)