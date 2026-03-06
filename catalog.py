import json
from pathlib import Path
from typing import Any, Dict, List

PROVIDERS_PATH = Path(__file__).parent / "providers.json"


def load_items() -> List[Dict[str, Any]]:
    with open(PROVIDERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])
