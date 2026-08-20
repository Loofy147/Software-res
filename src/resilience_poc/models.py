from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CRITICAL = {"functional", "dependency", "reproducibility", "concurrency", "security"}
REPRO_LEVELS = {"NOT_REPRODUCIBLE": 0, "REPRODUCIBLE": 1, "VERIFIED_REPRODUCIBLE": 2}

@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]


def decision_for_vector(vector: dict[str, Any], risk_tier: str = "low") -> dict[str, str]:
    """Deterministic policy engine: no aggregate score."""
    critical_fail = []
    critical_warn_or_unknown = []
    for dim in CRITICAL - {"reproducibility"}:
        status = vector.get(dim, {}).get("status", "unknown")
        if status == "fail":
            critical_fail.append(dim)
        elif status in {"warn", "unknown"}:
            critical_warn_or_unknown.append(dim)

    repro = vector.get("reproducibility", {}).get("level", "NOT_REPRODUCIBLE")
    mandatory_failed = bool(vector.get("mandatory_invariant_failures", []))

    if critical_fail or mandatory_failed or repro == "NOT_REPRODUCIBLE":
        return {"outcome": "REJECT", "rule": "critical_failure_or_unreproducible"}

    if critical_warn_or_unknown:
        return {"outcome": "REVIEW", "rule": "critical_dimensions_have_warn_or_unknown"}

    if risk_tier not in {"low", "medium"}:
        return {"outcome": "REVIEW", "rule": "risk_tier_disallows_automation"}

    return {"outcome": "AUTO_MERGE", "rule": "all_critical_dimensions_pass_and_reproducible"}
