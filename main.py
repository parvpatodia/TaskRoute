from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from planner import recommend_plan


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OptimizeRequest(BaseModel):
    task_type: str
    budget_usd: float
    objective: str
    current_provider: str | None = None
    state_tokens: int = 1200


@app.get("/")
def root():
    return {"ok": True, "service": "taskroute"}


@app.post("/optimize")
def optimize(req: OptimizeRequest):
    return recommend_plan(
        task_type=req.task_type,
        budget_usd=req.budget_usd,
        objective=req.objective,
        current_provider=req.current_provider,
        state_tokens=req.state_tokens
    )