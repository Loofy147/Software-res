"""Explicit epistemic states for software evidence.

This module deliberately separates evidence state from the policy status of a
Reliability Vector dimension.
"""
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

    Precedence:
      INVALID > CONFLICT > STALE > FAIL > PASS > UNOBSERVED.
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
    if any(r.get("state") == "FAIL" or r.get("status") == "fail" for r in rows):
        return EvidenceState.FAIL
    if all(r.get("state") == "PASS" or r.get("status") == "pass" for r in rows):
        return EvidenceState.PASS
    return EvidenceState.UNOBSERVED
