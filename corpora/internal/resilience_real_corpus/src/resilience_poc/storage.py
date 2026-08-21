from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[2]
STORE = BASE / "artifacts" / "store"
STORE.mkdir(parents=True, exist_ok=True)


def put_json(obj: dict[str, Any], artifact_id: str) -> Path:
    path = STORE / f"{artifact_id}.json"
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    return path


def get_json(artifact_id: str) -> dict[str, Any]:
    path = STORE / f"{artifact_id}.json"
    if not path.exists():
        raise FileNotFoundError(artifact_id)
    return json.loads(path.read_text(encoding="utf-8"))
