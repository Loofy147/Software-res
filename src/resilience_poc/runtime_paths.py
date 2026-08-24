from __future__ import annotations

import os
from pathlib import Path


def runtime_home() -> Path:
    configured = os.environ.get("RESILIENCE_POC_HOME")
    home = Path(configured).expanduser() if configured else Path.cwd() / ".resilience-poc"
    home.mkdir(parents=True, exist_ok=True)
    return home


HOME = runtime_home()
KEYS = HOME / "keys"
STORE = HOME / "artifacts" / "store"
KEYS.mkdir(parents=True, exist_ok=True)
STORE.mkdir(parents=True, exist_ok=True)
