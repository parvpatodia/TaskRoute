import os
from typing import Any, Dict, Optional

def explain_plan(payload: Dict[str, Any]) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        rec = payload["recommendation"]
        b = rec["breakdown"]
        return (
            f"Picked {rec['name']} on {rec['provider']} because it best matches {b['objective']} "
            f"after accounting for switching cost and reliability risk."
        )

    # keep simple for now, we will wire to OpenAI client after you confirm you want it
    rec = payload["recommendation"]
    b = rec["breakdown"]
    return (
        f"Picked {rec['name']} on {rec['provider']} because it best matches {b['objective']} "
        f"after accounting for switching cost and reliability risk."
    )