"""Explicit epistemic states for software evidence."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Iterable, Mapping


class EvidenceState(StrEnum):
    UNOBSERVED = "UNOBSERVED"
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"
    STALE = "STALE"
    CONFLICT = "CONFLICT"


def _expired(record: Mapping[str, Any], now: datetime | None) -> bool:
    expires_at = record.get("expires_at")
    if not expires_at or now is None:
        return False
    try:
        if expires_at.endswith("Z"):
            expires_at = expires_at[:-1] + "+00:00"
        return datetime.fromisoformat(expires_at) <= now
    except ValueError:
        return False


def assess_evidence(
    records: Iterable[Mapping[str, Any]],
    *,
    now: datetime | None = None,
) -> EvidenceState:
    """Classify evidence deterministically.

    Evidence state describes epistemic trust/observation, not the policy result.
    Therefore a warning is still observed evidence (PASS state), while a missing,
    stale, invalid, or conflicting record blocks positive inference.

    Precedence:
      INVALID > EXPLICIT_CONFLICT > STALE > DERIVED_CONFLICT > FAIL > UNOBSERVED > PASS.
    """
    rows = list(records)
    if not rows:
        return EvidenceState.UNOBSERVED

    if any(r.get("valid") is False or r.get("state") == "INVALID" for r in rows):
        return EvidenceState.INVALID

    if any(r.get("conflict") is True or r.get("state") == "CONFLICT" for r in rows):
        return EvidenceState.CONFLICT

    if any(r.get("stale") is True or r.get("state") == "STALE" or _expired(r, now) for r in rows):
        return EvidenceState.STALE

    observed_states = set()
    incomplete = False
    for record in rows:
        explicit = record.get("state")
        if explicit in {"PASS", "FAIL"}:
            observed_states.add(explicit)
            continue
        status = record.get("status")
        if status == "fail":
            observed_states.add("FAIL")
        elif status in {"pass", "warn"}:
            observed_states.add("PASS")
        else:
            incomplete = True

    if {"PASS", "FAIL"} <= observed_states:
        return EvidenceState.CONFLICT
    if "FAIL" in observed_states:
        return EvidenceState.FAIL
    if incomplete:
        return EvidenceState.UNOBSERVED
    if observed_states == {"PASS"}:
        return EvidenceState.PASS
    return EvidenceState.UNOBSERVED
