from __future__ import annotations

import os
from pathlib import Path

# Keep test artifacts/keys outside the package and source tree.
os.environ.setdefault("RESILIENCE_POC_HOME", str(Path.cwd() / ".test-resilience-poc"))
